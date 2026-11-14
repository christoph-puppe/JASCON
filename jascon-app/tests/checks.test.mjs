/* The Checks tool (CP-CHECK-1): jascon-checks.js, the check-draft part of
   jascon-ai.js, and the page in a browser.

   What they prove:
   - a model's answer becomes a Check only in code: the id is minted here,
     the requirement and clauses are the ones asked about, confidence is
     draft; an answer whose "expected" is not JSON, that names a parameter
     the rule does not have, or that writes a float, is refused with a reason;
   - what is drafted passes the same rules as a check written by hand;
   - the read-only lint flags the usual ways a script changes a system and
     leaves a plain reading script alone;
   - prompt, answer schema and kernel agree on the operators and fact types,
     and the prompt says \d and \"no\" literally (a template literal had
     swallowed the backslashes before the first push);
   - in a browser: a CIS catalog imported with "draft checks" hands over to
     the Checks tool, nothing is sent without a key and a click, a rule
     marked manual is never sent, the key travels only in the header and is
     in no storage, a draft the rules refuse cannot be saved, a draft that is
     taken is a valid Check, and the exported bundle passes the Python
     reference validator. The model is simulated; no real service is called. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { cisSynthetic } from "./cis-synthetic.mjs";

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const core = require("../jascon-core.js"), rules = require("../jascon-rules.js"), checks = require("../jascon-checks.js"), ai = require("../jascon-ai.js");
const { JSC_SCHEMA } = require("../jascon-schema.js");
const OPS = JSC_SCHEMA.$defs.checkOp.enum, TYPES = JSC_SCHEMA.$defs.checkFactType.enum;
let chromium = null;
try { ({ chromium } = require("playwright")); } catch (e) { /* the browser test is skipped */ }

/* ---------- assembling a Check from an answer ---------- */
const REQ = { id: "https://ex.org/req/SSH-1", version: "1", label: "SSH-1", lifecycle: "active", title: { en: "SSH" },
  statements: [{ id: "s1", modality: "must", "obligated-parties": ["https://ex.org/p"], prose: { en: "At most {param:max-tries} attempts." },
    parameters: [{ name: "max-tries", type: "integer", tightening: "lower" }] }] };
const ctx = (over = {}) => ({ req: REQ, statementIds: ["s1"], platform: "https://ex.org/platform", runtime: "bash", id: "https://my.example/check/ssh-1-bash",
  authorRef: "https://my.example/party/check-author", date: "2026-11-11", lang: "en", drafter: "gemini/gemini-3.8-flash", ...over });
const answer = (over = {}) => ({ fits: true, reason: "sshd -T reports the effective value.", each: "",
  facts: [{ name: "sshd.maxauthtries", type: "integer", cardinality: "one", description: "MaxAuthTries as sshd -T reports it" }],
  criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: '{"param": "max-tries"}' }], applies_when: [],
  collector: "sshd -T | awk '$1==\"maxauthtries\"{print \"{\\\"facts\\\":{\\\"sshd.maxauthtries\\\":\" $2 \"}}\"}'", ...over });

test("an answer becomes a Check in code: id, requirement, clauses and confidence are not the model's", () => {
  const res = checks.jscChecksFromAnswer(answer(), ctx());
  assert.deepEqual(res.problems, []);
  const c = res.check;
  assert.equal(c.id, "https://my.example/check/ssh-1-bash");
  assert.equal(c["requirement-ref"], REQ.id);
  assert.deepEqual(c["statement-ids"], ["s1"]);
  assert.equal(c.confidence, "draft");
  assert.equal(c.lifecycle, "draft");
  assert.deepEqual(c.criteria, [{ fact: "sshd.maxauthtries", op: "at-most", expected: { param: "max-tries" } }]);
  assert.equal(c.annotations["jascon-app"]["drafted-by"], "model");
  /* it is a Check, and the rules a hand-written check meets have nothing against it */
  assert.deepEqual(rules.jscMatchTypes(c), ["check"]);
  const objs = new Map([[REQ.id, { type: "requirement", obj: REQ }], [c.id, { type: "check", obj: c }]]);
  assert.deepEqual(rules.jscCheckObjectErrors(c.id, c, objs), []);
  assert.deepEqual(rules.jscCheckVerdict(c, { facts: { "sshd.maxauthtries": 5 } }, { "max-tries": 4 })[0], "not-satisfied");
});
test("an answer that cannot be assembled is refused with a reason, and one that does not fit makes no check", () => {
  const refuse = (over, frag) => {
    const res = checks.jscChecksFromAnswer(answer(over), ctx());
    assert.equal(res.check, null, frag);
    assert.ok(res.problems.some(p => p.includes(frag)), `${frag}: ${res.problems.join(" | ")}`);
  };
  refuse({ criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: "four" }] }, "not JSON");
  refuse({ criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: '{"param": "max_tries"}' }] }, "was not sent");
  refuse({ criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: "4.5" }] }, "JSON float");
  refuse({ criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: "" }] }, "needs a value");
  refuse({ collector: "  " }, "no collector source");
  const no = checks.jscChecksFromAnswer(answer({ fits: false, reason: "needs judgement" }), ctx());
  assert.deepEqual([no.fits, no.check, no.reason], [false, null, "needs judgement"]);
  /* a draft the assembly accepts can still be one the rules refuse: a pattern outside I-Regexp */
  const bad = checks.jscChecksFromAnswer(answer({ facts: [{ name: "x", type: "string", cardinality: "one", description: "" }],
    criteria: [{ fact: "x", op: "matches", expected: JSON.stringify("\\w+") }] }), ctx());
  const objs = new Map([[REQ.id, { type: "requirement", obj: REQ }]]);
  assert.deepEqual(rules.jscCheckObjectErrors(bad.check.id, bad.check, objs).map(([r]) => r), ["CHECK-6"]);
});
test("ids are minted under the organisation's namespace, unique in the set", () => {
  const taken = new Set(["https://my.example/check/ssh-1-bash"]);
  assert.equal(checks.jscChecksMintId("https://my.example/", REQ, "bash", taken), "https://my.example/check/ssh-1-bash-2");
  assert.equal(checks.jscChecksPlatform("https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/req/5.1.1", "https://my.example"),
    "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/platform");
});
test("the read-only lint flags what writes, installs, restarts or reaches out, and leaves a reading script alone", () => {
  const hits = src => checks.jscCollectorLint("bash", src).map(w => w.why);
  assert.deepEqual(hits("sshd -T 2>/dev/null | awk '$1==\"x\"{print $2}'\necho done >&2\n# rm -rf / in a comment"), []);
  for (const line of ["sed -i 's/a/b/' /etc/ssh/sshd_config", "echo x > /etc/issue", "systemctl restart sshd", "apt-get install -y auditd", "curl https://example.org", "chmod 600 /etc/shadow"]) {
    assert.ok(hits(line).length, line);
  }
  assert.ok(checks.jscCollectorLint("python", "open('/etc/x', 'w').write('y')").length);
  assert.ok(checks.jscCollectorLint("ansible", "- ansible.builtin.lineinfile:\n    path: /etc/ssh/sshd_config").length);
  assert.deepEqual(checks.jscCollectorLint("python", "print(open('/etc/ssh/sshd_config').read())"), []);
});
test("prompt, answer schema and kernel agree on operators and fact types; the prompt keeps its backslashes", () => {
  assert.equal(ai.jscAiCheckOps(OPS).split("\n").length, OPS.length, "every operator of the kernel is explained to the model");
  assert.deepEqual(Object.keys(ai.JSC_AI_CHECK_OPS).sort(), [...OPS].sort(), "and none that the kernel does not have");
  const schema = ai.jscAiCheckSchema(OPS, TYPES);
  const strict = (s, where) => {
    if (s.type === "object") {
      assert.equal(s.additionalProperties, false, where);
      assert.deepEqual([...s.required].sort(), Object.keys(s.properties).sort(), where);
      for (const [k, v] of Object.entries(s.properties)) strict(v, where + "." + k);
    } else if (s.type === "array") strict(s.items, where + "[]");
  };
  strict(schema, "check");
  assert.deepEqual(schema.properties.criteria.items.properties.op.enum, OPS);
  assert.deepEqual(schema.properties.facts.items.properties.type.enum, TYPES);
  const def = ai.JSC_PROMPTS.find(p => p.key === "check-draft").def;
  assert.ok(def.includes("no \\d \\w \\s \\b"), "the excluded escapes are named as they are written");
  assert.ok(def.includes('"\\"no\\""'), "a JSON string literal is shown escaped");
  assert.ok(!/[\x00-\x08]/.test(def), "no control character slipped in");
  assert.ok(def.trimEnd().endsWith("{rule}"), "the rule is the varying item, last");
});
test("the rule block names the clauses, the parameters with their bounds, and the audit text", () => {
  const params = checks.jscChecksParams(REQ, []);
  const text = ai.jscAiCheckRule({ req: REQ, statementIds: [], params, audit: "Run sshd -T.", remediation: "", description: "", text: v => (v && v.en) || "" });
  assert.ok(text.includes("clause s1 (must): At most {param:max-tries} attempts."));
  assert.ok(text.includes("parameters: max-tries (integer, tightening lower)"));
  assert.ok(text.includes("audit:\nRun sshd -T."));
});
test("the rules a set offers: the example folder's LNX-SSH-1 with its two checks", () => {
  const EX = path.join(ROOT, "jascon/examples");
  const objs = rules.jscTypedObjects(fs.readdirSync(EX).filter(f => f.endsWith(".json")).map(f => JSON.parse(fs.readFileSync(path.join(EX, f), "utf8"))).filter(o => o && o.id && !o["manifest-version"]));
  const row = checks.jscChecksRules(objs).find(r => r.id === "https://cso.example/req/LNX-SSH-1");
  assert.equal(row.checks.length, 2);
});

/* ---------- the page ---------- */
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
/* what the simulated model answers, by the rule in the prompt */
function simulated(prompt) {
  const sshd = { fits: true, reason: "sshd -T reports the effective MaxAuthTries.", each: "",
    facts: [{ name: "sshd.maxauthtries", type: "integer", cardinality: "one", description: "MaxAuthTries as sshd -T reports it" }],
    criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: "4" }], applies_when: [],
    collector: "#!/bin/bash\nv=$(sshd -T | awk '$1==\"maxauthtries\"{print $2}') || exit 1\nprintf '{\"facts\":{\"sshd.maxauthtries\":%s}}\\n' \"$v\"" };
  if (prompt.includes("description of the check:")) return { ...sshd, criteria: [{ fact: "sshd.maxauthtries", op: "at-most", expected: "3" }] };
  if (prompt.includes("title: 5.1.1")) return sshd;
  if (prompt.includes("title: 1.1.1")) return { ...sshd, facts: [{ name: "mount.options", type: "code", cardinality: "many", description: "" }],
    criteria: [{ fact: "mount.options", op: "matches", expected: JSON.stringify("\\w+") }], collector: "findmnt -no OPTIONS /tmp" };
  return { fits: false, reason: "This rule needs a person to judge it.", each: "", facts: [], criteria: [], applies_when: [], collector: "" };
}

test("checks page: from a CIS import to saved checks, with a simulated model", { skip: !chromium && "Playwright with Chromium is not installed" }, async () => {
  const KEY = "TEST-KEY-checks-must-not-be-stored-987654321";
  const server = await serve(), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
  const browser = await chromium.launch();
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-checks-"));
  try {
    const page = await (await browser.newContext()).newPage();
    const errors = [], sent = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, async route => {
      const req = route.request();
      if (!req.url().startsWith("https://generativelanguage.googleapis.com/")) { sent.push({ url: req.url() }); return route.abort(); }
      const body = req.postDataJSON(), prompt = body.contents[0].parts[0].text;
      sent.push({ url: req.url(), key: req.headers()["x-goog-api-key"], body, prompt });
      await route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*" }, contentType: "application/json",
        body: JSON.stringify({ candidates: [{ finishReason: "STOP", content: { parts: [{ text: JSON.stringify(simulated(prompt)) }] } }], usageMetadata: {} }) });
    });
    /* 1. import the catalog with "draft checks afterwards" */
    await page.goto(base + "index.html#import");
    const f = page.frameLocator("#app-frame");
    await f.locator("#btn-pick").waitFor({ timeout: 60000 });
    await f.locator("#pick").setInputFiles({ name: "cis-synthetic.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(cisSynthetic())) });
    assert.equal(await f.locator("#o-preset").inputValue(), "cis-benchmark", "the preset is guessed from the title");
    assert.equal(await f.locator("#o-ns").inputValue(), "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts");
    /* who states the cross-references and when, as the source has it: CIS, on the day the catalog was last changed; two fields that can be typed over */
    assert.deepEqual([await f.locator("#o-author").inputValue(), await f.locator("#o-date").inputValue()], ["https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/party/cis", "2026-11-11"]);
    await f.locator("#o-checks").check();
    await f.locator("#run").click();
    assert.match(await f.locator("#report-provenance").innerText(), /of 4 record\(s\) that can name an author: 4 as the source states it, 0 as entered here, 0 not stated/);
    await f.locator("#write").click();
    /* 2. the hub hands over to the Checks tool, on its drafting view, and nothing has been sent */
    await f.locator("#d-body .stmt .verdict-warn").waitFor({ timeout: 30000 });
    assert.ok(page.url().endsWith("#checks") || (await page.locator('#tabs [data-id="checks"].active').count()) === 1, "the Checks tab is shown");
    const chips = await f.locator("#d-body .chip").allInnerTexts();
    assert.ok(chips.some(c => /^3\s/.test(c) && /draft/.test(c)), "three automated rules to draft: " + chips.join(" | "));
    assert.ok(chips.some(c => /^2\s/.test(c) && /manual/.test(c)), "two marked manual, resolved without a model");
    assert.ok(await f.locator("#d-run").isDisabled(), "without a key nothing can be sent");
    assert.deepEqual(sent, []);
    /* 3. the key, the run */
    await f.locator("#d-access .ai-key").fill(KEY);
    await f.locator("#d-access .ai-key").dispatchEvent("change");
    await f.locator("#d-access .verdict-ok").waitFor();
    assert.deepEqual(sent, [], "typing the key sends nothing");
    await f.locator("#d-run").click();
    await f.locator("#log div", { hasText: "checks:" }).first().waitFor({ timeout: 30000 });
    assert.equal(sent.length, 3, "one call per automated rule, none for a manual one");
    assert.ok(sent.every(c => c.key === KEY && !c.url.includes(KEY) && !JSON.stringify(c.body).includes(KEY)), "the key travels in the header only");
    assert.ok(sent.every(c => !c.prompt.includes("1.1.2") && !c.prompt.includes("title: 5.9")), "the manual rules were not sent");
    assert.ok(sent.some(c => c.prompt.includes("Run sshd -T and verify that maxauthtries is 4 or less.")), "the audit text is what the model reads");
    assert.deepEqual(sent[0].body.generationConfig.responseJsonSchema.properties.criteria.items.properties.op.enum, OPS);
    /* 4. one passes, one is refused by the rules (a pattern outside I-Regexp), one does not fit */
    const rowText = id => f.locator(`[data-drow$="/req/${id}"]`).innerText();
    assert.match(await rowText("5.1.1"), /passes the rules/);
    assert.match(await rowText("1.1.1"), /CHECK-6/);
    assert.match(await rowText("5.2.1"), /does not fit/);
    assert.ok(await f.locator('[data-drow$="/req/1.1.1"] [data-pick]').isDisabled(), "a draft the rules refuse cannot be ticked");
    await f.locator("#d-tick").click();
    await f.locator("#d-save").click();
    await f.locator("#log .l-ok", { hasText: "saved 1 check(s)" }).waitFor({ timeout: 30000 });
    /* 5. the per-check path: a description for a rule in the editor, the draft fills the form, then it is saved */
    await f.locator('.navitem[data-view="rules"]').click();
    await f.locator('[data-new$="/req/5.2.1"]').click();
    await f.locator("#e-desc").fill("sshd must allow at most three authentication attempts.");
    await f.locator("#e-desc").dispatchEvent("change");
    await f.locator("#e-ai-run").click();
    await f.locator("#e-form .verdict-ok").waitFor({ timeout: 30000 });
    assert.equal(await f.locator('#e-form [data-row="criteria"] [data-k="expected"]').first().inputValue(), "3", "the draft filled the form");
    assert.equal(sent.length, 4);
    await f.locator("#e-save").click();
    await f.locator("#log .l-ok", { hasText: "saved check" }).waitFor({ timeout: 30000 });
    /* 6. what is in the set: two valid draft checks; the export pins kernel 2.0.0 */
    const state = await f.locator("body").evaluate(async () => {
      const g = jscSet.graph, cs = [...g.objects.values()].filter(r => r.type === "check").map(r => r.obj);
      const res = await jscCheckGraph(g, await jscVerify(g)), built = await jscBuildBundle(g);
      return { checks: cs, errors: res.findings.filter(x => x.kind === "error").map(x => `${x.object}: ${x.message}`), files: built.files, kernel: built.manifest["kernel-version"] };
    });
    assert.equal(state.checks.length, 2);
    assert.ok(state.checks.every(c => c.confidence === "draft" && c.annotations["jascon-app"]["drafted-by"] === "model"));
    assert.ok(state.checks.some(c => c["requirement-ref"].endsWith("/req/5.1.1")) && state.checks.some(c => c["requirement-ref"].endsWith("/req/5.2.1")));
    assert.deepEqual(state.errors, [], "the app's rules have nothing against the set");
    assert.equal(state.kernel, "2.0.0");
    /* 7. the key is in no storage */
    const dump = await f.locator("body").evaluate(async () => {
      let idb = "";
      for (const d of await indexedDB.databases()) {
        const db = await new Promise(r => { const q = indexedDB.open(d.name); q.onsuccess = () => r(q.result); });
        for (const s of db.objectStoreNames) idb += JSON.stringify(await new Promise(r => { const q = db.transaction(s).objectStore(s).getAll(); q.onsuccess = () => r(q.result); }));
        db.close();
      }
      return { local: JSON.stringify(Object.entries(localStorage)), session: JSON.stringify(Object.entries(sessionStorage)), idb, log: document.getElementById("log").innerText };
    });
    assert.ok(dump.local.includes("jsc:cfg:ai:cache"), "the dump saw the storage the app writes");
    for (const [where, text] of Object.entries(dump)) assert.ok(!text.includes(KEY), "the key is not in " + where);
    assert.deepEqual(errors, []);
    /* 8. the exported bundle, judged by the Python reference validator */
    for (const file of state.files) { const p = path.join(out, file.path); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, file.text); }
    const py = spawnSync("python3", [path.join(ROOT, "jascon/scripts/validate_core.py"), out], { encoding: "utf8" });
    if (py.status !== null && !/No module named 'jsonschema'/.test(py.stderr)) assert.equal(py.status, 0, (py.stdout || "").split("\n").slice(-25).join("\n") + py.stderr);
  } finally {
    await browser.close(); server.close();
    fs.rmSync(out, { recursive: true, force: true });
  }
});
