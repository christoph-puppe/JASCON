/* Tests of the model access (jascon-ai.js).

   Three groups:
     1. the call layer against a mocked fetch: what a request carries and
        does not carry, the continuation loop, which errors are tried again
        and how often, the pool;
     2. the pure functions around a call: prompts, schemas, and the checks
        that drop what the model returned but was never sent;
     3. the risk page in Chromium against a mocked service: nothing is sent
        without a key, the key is in the request header and in no storage,
        it survives a change of tool through the hub and is forgotten there,
        and a draft that is taken becomes a valid Risk.

   No test calls a real service; none could be reached from here and none
   may be needed to run the tests. Group 3 needs Playwright with Chromium
   and is skipped where that is missing. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const APP = path.join(ROOT, "jascon-app");
const ai = require("../jascon-ai.js");
const core = ai.jscAiCore;

/* ---------- a fetch that answers from a queue and records what it was sent ---------- */
const calls = [];
let queue = [];
const realFetch = globalThis.fetch;
test.before(() => {
  globalThis.fetch = async (url, init = {}) => {
    calls.push({ url: String(url), body: init.body ? JSON.parse(init.body) : null, headers: init.headers || {}, signal: init.signal });
    const r = queue.shift() ?? { ok: true, body: {} };
    if (r.throw) throw r.throw;
    return { ok: r.ok, status: r.status ?? 200, json: async () => r.body };
  };
});
test.after(() => { globalThis.fetch = realFetch; });
const reset = (...answers) => { calls.length = 0; queue = answers; core.state.cancel = false; };
const stop = text => ({ ok: true, body: { candidates: [{ finishReason: "STOP", content: { parts: [{ text }] } }], usageMetadata: { promptTokenCount: 7, candidatesTokenCount: 3 } } });
const cont = (text, token, reason = "CONTINUATION") => ({ ok: true, body: { candidates: [{ finishReason: reason, continuationToken: token, content: { parts: text == null ? [] : [{ text }] } }] } });
const fail = (status, message) => ({ ok: false, status, body: message ? { error: { message } } : {} });
const chat = text => ({ ok: true, body: { choices: [{ finish_reason: "stop", message: { content: text } }], usage: { prompt_tokens: 5, completion_tokens: 2 } } });
const cfg = (over = {}) => ({ backend: "gemini", model: "gemini-3.8-flash", level: "low", apiKey: "SECRET-KEY", schema: { type: "object" }, retries: 2, ...over });
/* runs fn with the waits between retries skipped */
async function fast(t, fn) {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  let done = false;
  const p = fn().then(v => { done = true; return { v }; }, e => { done = true; return { e }; });
  while (!done) { await new Promise(r => setImmediate(r)); t.mock.timers.tick(60000); }
  t.mock.timers.reset();
  const r = await p;
  if (r.e) throw r.e;
  return r.v;
}

/* ====================== 1. the call layer ====================== */
test("a Gemini request carries the key in a header only, a schema, a thinking level, and no sampling parameter", async () => {
  reset(stop('{"a":1}'));
  assert.equal(await core.geminiOnce("the prompt", cfg()), '{"a":1}');
  const c = calls[0], gc = c.body.generationConfig;
  assert.equal(c.url, "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent");
  assert.equal(c.headers["x-goog-api-key"], "SECRET-KEY");
  assert.ok(!c.url.includes("SECRET-KEY") && !JSON.stringify(c.body).includes("SECRET-KEY"), "the key is in neither the URL nor the body");
  for (const k of ["temperature", "topP", "topK", "candidateCount", "maxOutputTokens"]) assert.ok(!(k in gc), k + " is not sent");
  assert.ok(!("thinkingBudget" in gc.thinkingConfig));
  assert.equal(gc.thinkingConfig.thinkingLevel, "low");
  assert.equal(gc.responseMimeType, "application/json");
  assert.deepEqual(gc.responseJsonSchema, { type: "object" });
  assert.ok(c.signal instanceof AbortSignal, "the request has a timeout");
});

test("minimal thinking is sent only to the models that have it", () => {
  assert.equal(core.clampLevel("gemini-3.8-flash", "minimal"), "low");
  assert.equal(core.clampLevel("gemini-4-argon", "minimal"), "low");
  assert.equal(core.clampLevel("a-model-nobody-knows", "minimal"), "low");
  assert.equal(core.clampLevel("gemini-3.5-flash-lite", "minimal"), "minimal");
  assert.equal(core.clampLevel("gemini-4-argon", "high"), "high");
});

test("a continued answer is asked for with the same body and the token, and joined without a separator", async () => {
  reset(cont(null, "T1"), cont('{"items":[{"id":"R0', "T2"), stop('01"}]}'));
  assert.equal(await core.geminiOnce("p", cfg({ model: "gemini-4-argon" })), '{"items":[{"id":"R001"}]}');
  assert.equal(calls.length, 3);
  assert.ok(!("continuationToken" in calls[0].body));
  assert.equal(calls[1].body.continuationToken, "T1");
  assert.equal(calls[1].body.generationConfig.maxOutputTokens, 65536);
  assert.equal(calls[2].body.generationConfig.maxOutputTokens, 98304);
  assert.deepEqual(calls[2].body.contents, calls[0].body.contents, "the partial answer is never sent back");
  reset(cont("x", "A", "MAX_TOKENS"), cont("y", "B"), cont("z", "C"));
  await assert.rejects(() => core.geminiOnce("p", cfg()), /hops/);
  assert.equal(calls.length, 3, "the loop ends at its cap with a reason");
});

test("an answer without a candidate is an error that names the block reason", async () => {
  reset({ ok: true, body: { promptFeedback: { blockReason: "SAFETY" } } });
  await assert.rejects(() => core.geminiOnce("p", cfg()), e => /SAFETY/.test(e.message) && !core.isTransient(e));
});

test("OpenRouter and an own endpoint get a bearer token and a strict JSON schema; the thinking level is not sent", async () => {
  reset(chat('{"ok":true}'));
  assert.equal(await core.llmOnce("p", cfg({ backend: "openrouter", model: "vendor/model" })), '{"ok":true}');
  let c = calls[0];
  assert.equal(c.url, "https://openrouter.ai/api/v1/chat/completions");
  assert.equal(c.headers.Authorization, "Bearer SECRET-KEY");
  assert.deepEqual(c.body.response_format, { type: "json_schema", json_schema: { name: "result", strict: true, schema: { type: "object" } } });
  assert.deepEqual(c.body.provider, { require_parameters: true });
  for (const k of ["temperature", "top_p", "reasoning", "max_tokens"]) assert.ok(!(k in c.body), k + " is not sent");
  assert.ok(!c.url.includes("SECRET-KEY") && !JSON.stringify(c.body).includes("SECRET-KEY"));
  reset(chat("{}"));
  await core.llmOnce("p", cfg({ backend: "openai", model: "m", baseUrl: "https://llm.example/v1/" }));
  c = calls[0];
  assert.equal(c.url, "https://llm.example/v1/chat/completions");
  assert.ok(!("provider" in c.body) && !("X-Title" in c.headers));
  reset({ ok: true, body: { error: { code: 402, message: "insufficient credits" } } });
  await assert.rejects(() => core.llmOnce("p", cfg({ backend: "openrouter", model: "v/m" })), e => e.status === 402 && /credits/.test(e.message));
});

test("the service's own message reaches the caller; 4xx is permanent, 429, 5xx, a dropped connection and a timeout are not", async () => {
  reset(fail(400, "thinking_level minimal is not supported"));
  await assert.rejects(() => core.geminiOnce("p", cfg()), e => e.status === 400 && /minimal is not supported/.test(e.message) && !core.isTransient(e));
  for (const s of [401, 403, 404]) assert.ok(!core.isTransient(core.apiError(s, "x")), String(s));
  for (const s of [429, 500, 503]) assert.ok(core.isTransient(core.apiError(s, "x")), String(s));
  assert.ok(core.isTransient(new TypeError("fetch failed")));
  const timeout = new Error("t"); timeout.name = "TimeoutError";
  assert.ok(core.isTransient(timeout));
  assert.equal(core.apiError(500, "x".repeat(900)).message.length, 400, "a long message is cut");
});

test("a call is tried again after a transient error, within the setting, and never after a permanent one", async t => {
  reset(fail(429), stop("ok"));
  assert.equal(await fast(t, () => core.llm("p", cfg({ retries: 2 }), "t")), "ok");
  assert.equal(calls.length, 2);
  reset(fail(503), fail(503), fail(503), stop("never"));
  await assert.rejects(() => fast(t, () => core.llm("p", cfg({ retries: 2 }), "t")), e => e.status === 503);
  assert.equal(calls.length, 3, "one attempt and two retries");
  reset(fail(403, "no"), stop("never"));
  await assert.rejects(() => fast(t, () => core.llm("p", cfg({ retries: 5 }), "t")), e => e.status === 403);
  assert.equal(calls.length, 1);
});

test("no setting raises the retries above five", async t => {
  assert.equal(core.MAX_RETRIES, 5);
  reset(...Array.from({ length: 20 }, () => fail(500)));
  await assert.rejects(() => fast(t, () => core.llm("p", cfg({ retries: 50 }), "t")), e => e.status === 500);
  assert.equal(calls.length, 6, "one attempt and five retries");
});

test("an answer of the wrong shape is asked for again within the same budget", async t => {
  const shape = text => ai.jscAiRiskShape(core.extractJson(text));
  reset(stop('{"wrong":1}'), stop('{"risks":[]}'));
  assert.deepEqual(await fast(t, () => core.llm("p", cfg({ retries: 2 }), "t", shape)), { risks: [] });
  assert.equal(calls.length, 2);
  reset(stop("{}"), stop("{}"), stop("{}"), stop('{"risks":[]}'));
  await assert.rejects(() => fast(t, () => core.llm("p", cfg({ retries: 2 }), "t", shape)), /no list "risks"/);
  assert.equal(calls.length, 3);
});

test("a cancel stops the next call and the pool, and one task's error leaves the others running", async () => {
  reset(stop("x"));
  core.state.cancel = true;
  await assert.rejects(() => core.llm("p", cfg(), "t"), /cancelled/);
  assert.equal(calls.length, 0);
  core.state.cancel = false;
  let inflight = 0, peak = 0;
  const mk = i => async () => { inflight++; peak = Math.max(peak, inflight); await new Promise(r => setTimeout(r, 5)); inflight--; if (i === 2) throw new Error("boom"); return i; };
  const res = await core.runPool([0, 1, 2, 3, 4].map(mk), 2, () => {});
  assert.equal(peak, 2);
  assert.equal(res[2].error.message, "boom");
  assert.equal(res[4], 4);
  const seen = [];
  const res2 = await core.runPool([0, 1, 2, 3].map(i => async () => { seen.push(i); if (i === 0) core.state.cancel = true; return i; }), 1, () => {});
  assert.deepEqual(seen, [0]);
  assert.ok(res2.slice(1).every(r => r.cancelled));
  core.state.cancel = false;
});

test("JSON is found inside fences and prose", () => {
  assert.deepEqual(core.extractJson('```json\n{"a":1}\n```'), { a: 1 });
  assert.deepEqual(core.extractJson('Here: {"a":[1,2]} thanks'), { a: [1, 2] });
  assert.throws(() => core.extractJson("no json here"));
});

/* ====================== 2. prompts, schemas, checks ====================== */
const text = v => (typeof v === "string" ? v : (v && (v.en || Object.values(v)[0])) || "");

test("every default prompt has its needed placeholders, the stable part before the varying item", () => {
  for (const p of ai.JSC_PROMPTS) {
    for (const ph of p.need) assert.ok(p.def.includes(ph), `${p.key} has ${ph}`);
    for (const ph of p.need) assert.ok(p.append[ph], `${p.key} knows the heading for ${ph}`);
    const used = [...p.def.matchAll(/\{(\w+)\}/g)].map(m => `{${m[1]}}`);
    for (const ph of used) assert.ok([...p.need, ...p.also].includes(ph), `${p.key}: ${ph} is declared`);
  }
  const treat = ai.JSC_PROMPTS.find(p => p.key === "risk-treat").def;
  assert.ok(treat.indexOf("{candidates}") < treat.indexOf("{risk}"), "the candidates are the prefix every call of a run shares");
  assert.ok(treat.trimEnd().endsWith("{risk}"), "the risk is the last thing in the prompt");
});

test("a template that lost a placeholder gets it appended, an empty one is the default", () => {
  const vars = { candidates: "Q1 | a | b | c", risk: "R: something", max: 5, lang: "en" };
  const cut = ai.jscPromptFill("risk-treat", "Pick the right ones.", vars);
  assert.deepEqual(cut.appended, ["{candidates}", "{risk}"]);
  assert.ok(cut.text.includes("Q1 | a | b | c") && cut.text.endsWith("RISK\nR: something"));
  assert.deepEqual(ai.jscPromptMissing("risk-treat", "Pick. {candidates}"), ["{risk}"]);
  const def = ai.jscPromptFill("risk-treat", "   ", vars);
  assert.deepEqual(def.appended, []);
  assert.ok(def.text.includes("At most 5 requirements") && !/\{(candidates|risk|max|lang)\}/.test(def.text));
  /* text of the set that happens to contain braces is data, not a placeholder to fill again */
  assert.ok(ai.jscPromptFill("risk-treat", "", { ...vars, candidates: "Q1 | {risk} | x | y" }).text.includes("Q1 | {risk} | x | y"));
});

/* strict mode of the chat-completions services: every object closed, every property required */
function assertStrict(schema, where) {
  if (schema.type === "object") {
    assert.equal(schema.additionalProperties, false, where + " is closed");
    assert.deepEqual([...schema.required].sort(), Object.keys(schema.properties).sort(), where + " requires all its properties");
    for (const [k, v] of Object.entries(schema.properties)) assertStrict(v, where + "." + k);
  } else if (schema.type === "array") assertStrict(schema.items, where + "[]");
}
test("the answer schemas are strict, and a rating is asked for only on pinned scales and only in their codes", () => {
  const rated = ai.jscAiRiskSchema(["rare", "likely"], ["minor", "major"]);
  assertStrict(rated, "risks"); assertStrict(ai.JSC_AI_TREAT_SCHEMA, "treatments");
  assert.deepEqual(rated.properties.risks.items.properties.likelihood.enum, ["rare", "likely"]);
  const unrated = ai.jscAiRiskSchema([], []);
  assertStrict(unrated, "risks");
  assert.ok(!("likelihood" in unrated.properties.risks.items.properties) && !("impact" in unrated.properties.risks.items.properties));
});

const scale = (id, codes) => ({ id, levels: codes.map(c => ({ level: c, label: { en: c.toUpperCase() } })) });
test("what is sent for risk drafts names components by key and the scales by their codes", () => {
  const inp = ai.jscAiRiskInput({ context: "A small office.", count: 5, lang: "en", text,
    components: [{ id: "https://x/c/server", label: "SRV", title: { en: "File server" }, kind: "hardware" }],
    risks: [{ label: "R-1", title: { en: "Fire" }, scenario: { en: "The office burns." } }],
    lScale: scale("https://x/s/l", ["rare", "likely"]), iScale: scale("https://x/s/i", ["minor", "major"]) });
  assert.equal(inp.compKeys.get("C1"), "https://x/c/server");
  assert.ok(inp.vars.context.includes("A small office.") && inp.vars.context.includes("C1: SRV - File server (hardware)"));
  assert.ok(!inp.vars.context.includes("https://x/c/server"), "ids of the set are not sent, keys are");
  assert.equal(inp.vars.likelihood, "rare: RARE\nlikely: LIKELY");
  assert.ok(inp.vars.existing.includes("R-1: Fire - The office burns."));
  const bare = ai.jscAiRiskInput({ context: "", count: 5, lang: "en", text, components: [], risks: [], lScale: null, iScale: null });
  assert.ok(/no scale is pinned/.test(bare.vars.likelihood) && bare.vars.existing === "(none)");
  assert.ok(!("likelihood" in bare.schema.properties.risks.items.properties));
});

test("a risk draft keeps only what was sent: unknown component keys and level codes go, duplicates and empty drafts are dropped", () => {
  const sent = { compKeys: new Map([["C1", "https://x/c/server"]]), lCodes: ["rare", "likely"], iCodes: ["minor", "major"], existingTitles: ["Fire in the office"] };
  const res = ai.jscAiRiskCheck({ risks: [
    { title: "Ransomware", scenario: "Files are encrypted.", components: ["C1", "C7", "https://evil/c"], likelihood: "likely", impact: "major", reason: "common" },
    { title: " ransomware ", scenario: "Again.", components: [], likelihood: "rare", impact: "minor", reason: "" },
    { title: "FIRE in the office", scenario: "Burns.", components: [], likelihood: "rare", impact: "minor", reason: "" },
    { title: "", scenario: "Nothing.", components: [], likelihood: "rare", impact: "minor", reason: "" },
    { title: "Flood", scenario: "Water.", components: "C1", likelihood: "certain", impact: "major", reason: "x" },
  ] }, sent);
  assert.deepEqual(res.risks.map(r => r.title), ["Ransomware", "Flood"]);
  assert.deepEqual(res.risks[0].components, ["https://x/c/server"]);
  assert.match(res.risks[0].notes[0], /unknown component key removed: C7, https:\/\/evil\/c/);
  assert.equal(res.risks[0].likelihood, "likely");
  assert.ok(!("likelihood" in res.risks[1]) && !("impact" in res.risks[1]), "a code the scale does not have gives no rating");
  assert.deepEqual(res.risks[1].components, []);
  assert.deepEqual(res.dropped.map(d => d.why), ["duplicate", "duplicate", "empty"]);
  assert.throws(() => ai.jscAiRiskCheck({ risk: [] }, sent), e => e.badOutput === true);
  assert.throws(() => ai.jscAiRiskCheck(null, sent), e => e.badOutput === true);
});

test("candidates are cut into slices with keys that are unique across the run", () => {
  const reqs = Array.from({ length: 5 }, (v, i) => ({ id: "https://x/req/" + i, label: "L" + i, title: { en: "Title " + i }, prose: "Text   with\nbreaks " + i }));
  const slices = ai.jscAiCandidates(reqs, 2, text);
  assert.equal(slices.length, 3);
  assert.deepEqual(slices.flatMap(s => [...s.keys.keys()]), ["Q1", "Q2", "Q3", "Q4", "Q5"]);
  assert.equal(slices[2].keys.get("Q5"), "https://x/req/4");
  assert.equal(slices[0].text, "Q1 | L0 | Title 0 | Text with breaks 0\nQ2 | L1 | Title 1 | Text with breaks 1");
  assert.ok(!slices[0].text.includes("https://x/req/"), "ids of the set are not sent, keys are");
  assert.equal(ai.jscAiCandidates([], 2, text).length, 0);
});

test("a treatment suggestion keeps only keys that were sent in that call, once, and not what the risk names already", () => {
  const keys = new Map([["Q1", "https://x/req/a"], ["Q2", "https://x/req/b"], ["Q3", "https://x/req/c"]]);
  const res = ai.jscAiTreatCheck({ treatments: [
    { requirement: "Q2", reason: "acts on it" }, { requirement: "Q9", reason: "invented" }, { requirement: "https://x/req/a", reason: "an id, not a key" },
    { requirement: " Q3 ", reason: "already there" }, { requirement: "Q2", reason: "twice" }, { requirement: "Q1", reason: "also" } ] },
    { keys, already: new Set(["https://x/req/c"]) });
  assert.deepEqual(res.treatments, [{ id: "https://x/req/b", reason: "acts on it" }, { id: "https://x/req/a", reason: "also" }]);
  assert.equal(res.unknown, 2);
  assert.equal(res.known, 2);
  assert.throws(() => ai.jscAiTreatCheck({}, { keys, already: new Set() }), e => e.badOutput === true);
});

test("the estimate counts calls and characters", () => {
  assert.deepEqual(ai.jscAiEstimate(["abcd", "abcdefgh"]), { calls: 2, chars: 12, tokens: 3 });
});

test("the source keeps a key out of every storage and every URL", () => {
  const src = fs.readFileSync(path.join(APP, "jascon-ai.js"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  assert.ok(!/sessionStorage|indexedDB|document\.cookie/.test(src), "no storage but localStorage is touched");
  const written = [...src.matchAll(/localStorage\.setItem\(([^,]+),/g)].map(m => m[1].trim());
  assert.deepEqual([...new Set(written)].sort(), ["CACHE_KEY", "PROMPT_PREFIX + key"], "localStorage gets prompts and cached answers, nothing else");
  assert.ok(!/[?&]key=/.test(src), "no key in a query string");
  const hub = fs.readFileSync(path.join(APP, "index.html"), "utf8");
  const relay = hub.slice(hub.indexOf("const aiKeys"), hub.indexOf("/* ---------- start"));
  assert.ok(relay.length > 200 && !/localStorage|sessionStorage|indexedDB|jscCfg|jscStore/.test(relay), "the hub holds the key in a variable only");
});

/* ====================== 3. the risk page against a mocked service ====================== */
let chromium = null;
try { ({ chromium } = require("playwright")); } catch (e) { /* skipped below */ }
const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".md": "text/markdown" };
function serve() {
  const server = http.createServer((req, res) => {
    const file = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "content-type": MIME[path.extname(file)] || "application/octet-stream" });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, "127.0.0.1", () => resolve(server)));
}

test("risk page: nothing is sent without a key; the key stays in memory; a draft that is taken is a valid Risk", { skip: !chromium && "Playwright with Chromium is not installed" }, async () => {
  const KEY = "TEST-KEY-that-must-not-be-stored-0123456789";
  const server = await serve(), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
  const browser = await chromium.launch();
  try {
    const page = await (await browser.newContext()).newPage();
    const errors = [], sent = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, async route => {
      const req = route.request();
      if (!req.url().startsWith("https://generativelanguage.googleapis.com/")) { sent.push({ url: req.url() }); return route.abort(); }
      const body = req.postDataJSON(), prompt = body.contents[0].parts[0].text;
      sent.push({ url: req.url(), key: req.headers()["x-goog-api-key"], body, prompt });
      const p = body.generationConfig.responseJsonSchema.properties;
      const answer = p.treatments
        ? { treatments: [{ requirement: "Q1", reason: "acts on it" }, { requirement: "Q987654", reason: "invented" }] }
        : { risks: [{ title: "Ransomware encrypts the shares", scenario: "An attacker encrypts the file shares. Work stops.", components: ["C1", "C987654"],
            likelihood: p.risks.items.properties.likelihood.enum.at(-1), impact: p.risks.items.properties.impact.enum.at(-1), reason: "Common." }] };
      await route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*" }, contentType: "application/json",
        body: JSON.stringify({ candidates: [{ finishReason: "STOP", content: { parts: [{ text: JSON.stringify(answer) }] } }], usageMetadata: {} }) });
    });
    await page.goto(base + "index.html#load=../converted_examples/US.IFA-GoodRead/ifa-core-bundle/&tool=risk");
    await page.waitForFunction(() => document.querySelector("#home-log .l-ok"), null, { timeout: 60000 });
    const f = page.frameLocator("#app-frame");
    await f.locator("#log .l-ok").first().waitFor({ timeout: 30000 });
    await f.locator('.navitem[data-view="scales"]').click();
    await f.locator('[data-preset="0"][data-copy="1"]').click();
    await f.locator("#log .l-ok", { hasText: "added 3" }).waitFor();
    await f.locator('.navitem[data-view="model"]').click();
    await f.locator("#ai-context").fill("A small office with one file server.");
    await f.locator("#ai-context").dispatchEvent("change");
    await f.locator("#ai-owner").fill("https://example.org/my/party/ciso");
    await f.locator("#ai-owner").dispatchEvent("change");

    assert.ok(await f.locator("#ai-a-run").isDisabled() && await f.locator("#ai-b-run").isDisabled(), "without a key no call can be started");
    assert.deepEqual(sent, [], "nothing left the browser while the page was used without a key");

    await f.locator(".ai-key").fill(KEY);
    await f.locator(".ai-key").dispatchEvent("change");
    await f.locator("#ai-access .verdict-ok").waitFor();
    assert.equal(await f.locator(".ai-key").inputValue(), "", "the field does not keep the key on show");
    assert.deepEqual(sent, [], "typing the key sends nothing");
    await f.locator("#ai-a-run").click();
    await f.locator("#log .l-ok", { hasText: "draft(s) of risks" }).waitFor({ timeout: 30000 });
    assert.equal(sent.length, 1);
    assert.equal(sent[0].key, KEY, "the key travels in the header");
    assert.ok(!sent[0].url.includes(KEY) && !JSON.stringify(sent[0].body).includes(KEY), "and in neither the URL nor the body");
    assert.ok(sent[0].prompt.includes("A small office with one file server."));

    /* a draft taken while the owner field is empty: the kernel requires owner-ref on a Risk, so nothing is saved, and the
       page says so in its own words. A short name typed then is a party under the namespace (backlog #70) */
    await f.locator("#ai-owner").fill("");
    await f.locator("#ai-owner").dispatchEvent("change");
    await f.locator('[data-ai-save="0"]').click();
    await f.locator("#ai-a .stmt .verdict-bad").first().waitFor({ timeout: 30000 });
    assert.deepEqual(await f.locator("#ai-a .stmt .verdict-bad").allInnerTexts(),
      ["✗ No owner is named. The kernel requires owner-ref on a Risk, so the risk cannot be saved. The field “Owner” is empty. Name a party: a URI, or a short name, which becomes a party under your namespace."]);
    assert.equal(await f.locator("body").evaluate(() => [...jscSet.graph.objects.values()].filter(x => x.type === "risk" && (x.obj.annotations || {})["jascon-app"]).length), 0, "no draft was saved");
    assert.equal(await f.locator("#ai-owner").inputValue(), "", "and the field stays empty");
    await f.locator("#ai-owner").fill("ciso");
    await f.locator("#ai-owner").dispatchEvent("change");
    assert.equal(await f.locator("#ai-owner").inputValue(), "https://example.org/my/party/ciso");

    await f.locator('[data-ai-save="0"]').click();
    await f.locator("#ai-a .stmt .verdict-ok").waitFor({ timeout: 30000 });
    const saved = await f.locator("body").evaluate(async () => {
      const g = jscSet.graph, r = [...g.objects.values()].find(x => x.type === "risk" && (x.obj.annotations || {})["jascon-app"]);
      const scales = jscMatrixErrors(new Map([...g.scales].map(([id, x]) => [id, x.def]))).usable, sd = scales.get(r.obj.rating["scale-ref"]);
      const check = await jscCheckGraph(g, await jscVerify(g));
      return { obj: r.obj, cell: jscMatrixCell(sd, r.obj.rating.likelihood.level, r.obj.rating.impact.level), components: [...g.objects.values()].filter(x => x.type === "component").length,
        errors: check.findings.filter(x => x.kind === "error" && x.object === r.obj.id).map(x => x.message) };
    });
    assert.equal(saved.obj.state, "identified");
    assert.equal(saved.obj.lifecycle, "draft");
    assert.equal(saved.obj.rating.level, saved.cell, "the level is the matrix cell, computed, not the model's");
    assert.equal(saved.obj.annotations["jascon-app"]["drafted-by"], "model");
    assert.equal((saved.obj["component-refs"] || []).length, saved.components ? 1 : 0, "the key that was not sent named no component");
    assert.deepEqual(saved.errors, [], "the rules of the app have nothing against the saved Risk");

    await f.locator("#ai-b-run").click();
    await f.locator("#log div", { hasText: "treatments:" }).first().waitFor({ timeout: 30000 });
    assert.ok((await f.locator("#ai-b [data-ai-row]").first().innerText()).includes("1 key(s) the model returned were not among those sent"));
    const rows = await f.locator("#ai-b [data-ai-row]").count();
    assert.ok(rows >= 1);
    assert.equal(await f.locator("#ai-b [data-ai-pick]").count(), rows, "one requirement is offered per risk: the key that was sent");
    assert.ok(sent.slice(1).every(c => c.key === KEY && !c.url.includes(KEY)));

    const dump = await f.locator("body").evaluate(async () => {
      let idb = "";
      for (const d of await indexedDB.databases()) {
        const db = await new Promise(r => { const q = indexedDB.open(d.name); q.onsuccess = () => r(q.result); });
        for (const s of db.objectStoreNames) idb += JSON.stringify(await new Promise(r => { const q = db.transaction(s).objectStore(s).getAll(); q.onsuccess = () => r(q.result); }));
        db.close();
      }
      return { local: JSON.stringify(Object.entries(localStorage)), session: JSON.stringify(Object.entries(sessionStorage)), idb, log: document.getElementById("log").innerText,
        html: document.documentElement.outerHTML, cookie: document.cookie };
    });
    assert.ok(dump.local.includes("jsc:cfg:ai:cache"), "the dump saw the storage the app writes");
    for (const [where, text2] of Object.entries(dump)) assert.ok(!text2.includes(KEY), "the key is not in " + where);
    assert.ok(!(await page.content()).includes(KEY), "nor in the hub's document");

    /* the hub holds it across a change of tool, and forgets it on request */
    await page.click('#tabs [data-id="browse"]');
    await f.locator(".navitem[data-view]").first().waitFor({ timeout: 30000 });
    await page.click('#tabs [data-id="risk"]');
    await f.locator('.navitem[data-view="model"]').click();
    await f.locator("#ai-access .verdict-ok").waitFor({ timeout: 30000 });
    assert.ok(await f.locator("#ai-a-run").isEnabled());
    await page.click("#key-pill");
    await f.locator("#ai-access .hint[role=status]").waitFor();
    assert.ok(await f.locator("#ai-a-run").isDisabled(), "forgotten in the hub is forgotten in the tool");
    await page.reload();
    await page.click('#tabs [data-id="risk"]');
    await f.locator('.navitem[data-view="model"]').click();
    await f.locator("#ai-access [role=status]").waitFor({ timeout: 30000 });
    assert.ok(await f.locator("#ai-a-run").isDisabled() && await page.locator("#key-pill").isHidden(), "a reload asks for the key again");
    assert.deepEqual(errors, []);
  } finally { await browser.close(); server.close(); }
});
