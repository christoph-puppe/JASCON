/* JASCON-App model access: the one place from which a page calls a language
   model, and what the risk page asks one.

   Nothing in the app needs a model. Everything a rule or a lookup can answer
   is answered in code (jascon-rules.js); a model is asked only for the two
   things no rule can compute: a draft of risk scenarios for a described
   scope, which of the selected requirements act on a given risk, and a
   draft of a machine check (facts, criteria, collector code) for a
   technical rule. A model
   answer is a suggestion: it is checked here against what was sent, shown,
   and written into the set only when a person takes it.

   Data flow of a call:
     page builds the prompt from an editable template (JSC_PROMPTS)
       -> jscAi.ask() looks the prompt up in the answer cache
       -> llm() in the core block below: one call with a retry budget
       -> the answer is parsed, its shape checked (a wrong shape is asked
          again within the same budget), cached and returned
       -> the page checks every key the model returned against the keys that
          were sent (jscAiRiskCheck, jscAiTreatCheck) and drops the rest.

   Invariants:
     - The key of a model service is a secret. It lives in one variable of
       this page and, when the page runs inside the hub, in one variable of
       the hub, so that it survives a change of tool. It is never written to
       localStorage, sessionStorage, IndexedDB, a set, an export, a log line
       or a URL. A reload of the hub clears it and it is typed again.
     - The model never mints an identifier. It sees short keys (C1, Q7) that
       stand for the ids of the set; an answer with a key that was not sent
       loses that key.
     - No sampling parameters are sent. Two runs may differ; whatever must be
       identical between runs is computed in code.
     - At most MAX_RETRIES (5) retries per call, for transient errors and for
       an answer of the wrong shape together. Permanent errors (400, 401,
       403, 404) raise at once with the service's own message.

   The block between the two core markers is free of the DOM and of every
   other part of the app: tests/ai.test.mjs runs it under node with a mocked
   fetch. Keep it self-contained; schemas reach it through cfg.schema.

   Threat model of the key relay: the page hands the key to its parent
   window only by postMessage. Served over http(s) the message is addressed
   to the page's own origin, so a foreign page that frames a tool receives
   nothing. Opened as local files every page has the same opaque origin and
   the message cannot be addressed; a hostile local file that frames a tool
   page could then read a key typed there. The app does not defend against
   hostile files on the same disk.

   Not here: a second model pass that audits the first (a person reviews
   every suggestion instead), a price table (prices change faster than this
   file; the estimate is in calls and tokens), a live model list, streaming,
   search grounding, and a fallback for an endpoint that rejects a JSON
   schema. */
"use strict";

/* ====================================================================
   Pure part: prompts, schemas, building what is sent, checking what
   comes back. No DOM, no network.
   ==================================================================== */
/* N marks a text for translation (jascon-core.js). Under node this file is
   loaded without the core, so the marker is supplied here. */
if (typeof N === "undefined") globalThis.N = s => s;

const JSC_AI_BACKENDS = {
  gemini: { label: "Google Gemini", host: "generativelanguage.googleapis.com" },
  openrouter: { label: "OpenRouter", host: "openrouter.ai" },
  openai: { label: N("OpenAI-compatible endpoint"), host: "" },
};
const JSC_AI_LEVELS = ["minimal", "low", "medium", "high"];

/* ---------- prompts ----------
   Every text the app sends to a model starts as one of these templates. The
   text here is the default and the target of "reset"; the text in use is the
   one in the editor (settings page and the page that sends it), kept in
   localStorage under jsc:cfg:prompt:<key>. `need` are the placeholders
   without which the prompt is useless; a template that lost one gets it
   appended when the prompt is built. `also` are the other placeholders the
   page fills. The order of `need` is the order in which they are appended,
   stable content before the varying item. */
const JSC_PROMPTS = [
  { key: "risk-suggest", label: N("Prompt: suggest risks"), need: ["{context}"],
    also: ["{existing}", "{likelihood}", "{impact}", "{count}", "{lang}"],
    append: { "{context}": "SCOPE" },
    def: `You are an information security risk analyst. You draft risk scenarios for a risk register. A person reviews every draft before it is used.

TASK
Propose up to {count} risks for the scope described under SCOPE that the register under EXISTING RISKS does not contain yet.

RULES
- One risk is one scenario: what could happen, to what, with which consequence. Two to four sentences, concrete to this scope. No textbook risk that would fit any organisation unchanged.
- Do not repeat or rephrase an existing risk.
- Do not propose measures. The scenario describes the risk before any treatment.
- "components": the keys (C1, C2, ...) of the components listed under SCOPE that the risk concerns. Use only keys that are listed. An empty list when none fits or none is listed.
- "likelihood" and "impact": one code of the scales below, judged for the scope as described and before any treatment. Where the description gives no basis for a judgement, choose the middle of the scale and say so in "reason".
- "reason": one or two sentences on why this risk matters for this scope and how you judged likelihood and impact.
- Write title, scenario and reason in the language "{lang}".

LIKELIHOOD SCALE (code: meaning, lowest first)
{likelihood}

IMPACT SCALE (code: meaning, lowest first)
{impact}

EXISTING RISKS
{existing}

SCOPE
{context}` },
  { key: "risk-treat", label: N("Prompt: suggest treatments"), need: ["{candidates}", "{risk}"],
    also: ["{max}", "{lang}"],
    append: { "{candidates}": "REQUIREMENTS (key | label | title | text)", "{risk}": "RISK" },
    def: `You are an information security risk analyst. You match one risk to the requirements that treat it. A person reviews every match before it is used.

TASK
From the REQUIREMENTS below, pick those whose fulfilment directly lowers the likelihood or the impact of the RISK at the end.

RULES
- Use only the keys listed under REQUIREMENTS (Q1, Q2, ...). Never invent a key.
- Pick a requirement only when you can say in one sentence how it acts on this risk. A requirement that is merely good practice, or only loosely related, is not a match.
- At most {max} requirements, the most direct first. An empty list is a valid answer.
- "reason": one sentence on how the requirement acts on the risk, in the language "{lang}".

REQUIREMENTS (key | label | title | text)
{candidates}

RISK
{risk}` },
  { key: "check-draft", label: N("Prompt: draft a check"), need: ["{rule}"],
    also: ["{runtime}", "{platform}", "{facttypes}", "{ops}", "{lang}"],
    append: { "{rule}": "RULE" },
    def: `You are a security engineer. You turn one technical rule into a machine check. A person reviews every draft before it is used.

A CHECK HAS TWO PARTS
1. A collector: a {runtime} program that runs on the target ({platform}), reads the effective state and prints exactly one line of JSON: {"facts": {...}}, or {"resources": [{"id": "...", "facts": {...}}, ...]} when the rule is about each of many things (files, accounts, mounts). The collector decides nothing.
2. Criteria: a flat list of assertions that must ALL hold. Each assertion compares one fact with one operator. Nothing else decides pass or fail.

COLLECTOR RULES
- Read only. Never change the system: no writes, no installs, no service changes, no edits of configuration. No network access.
- Report effective values: what the running system uses, with defaults resolved and include files merged (for example "sshd -T", not the config file).
- A fact you looked for and did not find is left out of "facts". If the program cannot look at all (command missing, permission denied), it exits with a non-zero status and prints nothing.
- Numbers as JSON numbers, booleans as true or false, decimals as strings like "1.5", lists as JSON arrays of strings.
- Short and plain.

FACT TYPES
{facttypes}
A fact is one value, or a list when its cardinality is "many".

OPERATORS (there are no others)
{ops}

EXPECTED
- "expected" is JSON text: a literal of the fact's type ("4", "\\"no\\"", "true", "[\\"a\\", \\"b\\"]"), or {"param": "<name>"} for a parameter listed under RULE. When the rule has a parameter for the threshold, use it, never its default.
- present and absent take no value: "expected" is "".
- matches and matches-not take an I-Regexp pattern (RFC 9485) that must match the WHOLE value: no anchors, no \\d \\w \\s \\b, no lookaround, no back-references, no flags. Write [0-9], [ \\t], and explicit alternatives instead.

WHEN IT DOES NOT FIT
A rule that needs human judgement, a comparison between two facts, arithmetic, or an OR across different facts cannot be a check. Then "fits" is false, "reason" says why, and the other fields are empty.

ANSWER
"fits"; "reason": one or two sentences in the language "{lang}"; "each": the kind of resource when the rule is about each of many things, else ""; "facts": name, type, cardinality ("one" or "many"), description; "criteria": fact, op, expected; "applies_when": assertions that must hold for the rule to apply at all, else an empty list; "collector": the {runtime} source.

RULE
{rule}` },
];

/* The prompt that is sent: the template with its placeholders filled. An
   empty template is the default; a needed placeholder the template lost is
   appended under its heading, so an edit can never produce a prompt without
   the data. Returns the text and the placeholders that had to be appended. */
function jscPromptFill(key, template, vars) {
  const p = JSC_PROMPTS.find(x => x.key === key);
  if (!p) throw new Error("unknown prompt " + key);
  let tpl = String(template || "").trim() ? String(template) : p.def;
  const appended = p.need.filter(ph => !tpl.includes(ph));
  for (const ph of appended) tpl += `\n\n${p.append[ph]}\n${ph}`;
  const text = tpl.replace(/\{(\w+)\}/g, (m, name) => (Object.prototype.hasOwnProperty.call(vars, name) ? String(vars[name]) : m));
  return { text, appended };
}
const jscPromptMissing = (key, template) => {
  const p = JSC_PROMPTS.find(x => x.key === key);
  return String(template || "").trim() ? p.need.filter(ph => !String(template).includes(ph)) : [];
};

const jscAiOneLine = (s, max) => {
  const t = String(s || "").replace(/\s+/g, " ").trim();
  return max && t.length > max ? t.slice(0, max - 1) + "…" : t;
};

/* ---------- pass A: suggest risks ---------- */

/* The answer schema. Likelihood and impact are asked only when the set pins
   the scales to state them on, and then as an enum of the codes that exist.
   Every property is required and no other is allowed, which is what the
   strict mode of the chat-completions services demands. */
function jscAiRiskSchema(lCodes, iCodes) {
  const props = { title: { type: "string" }, scenario: { type: "string" }, components: { type: "array", items: { type: "string" } } };
  if (lCodes.length && iCodes.length) {
    props.likelihood = { type: "string", enum: lCodes };
    props.impact = { type: "string", enum: iCodes };
  }
  props.reason = { type: "string" };
  return { type: "object", additionalProperties: false, required: ["risks"], properties: { risks: { type: "array",
    items: { type: "object", additionalProperties: false, required: Object.keys(props), properties: props } } } };
}
const jscAiLevelLines = (scale, text) => (scale ? scale.levels.map(l =>
  `${l.level}: ${[text(l.label), text(l.description)].filter(Boolean).map(s => jscAiOneLine(s, 200)).join(" - ") || l.level}`).join("\n") : "");

/* What pass A sends, from the set and the description the user typed.
   components: [{id, label, title, kind}], risks: [{label, title, scenario}],
   lScale / iScale: scale definitions or null, text: language-map reader.
   Returns the placeholder values, the schema and the key table. */
function jscAiRiskInput({ context, components, risks, lScale, iScale, count, lang, text }) {
  const compKeys = new Map(components.map((c, i) => ["C" + (i + 1), c.id]));
  const compLines = components.map((c, i) => `C${i + 1}: ${jscAiOneLine([c.label, text(c.title)].filter(Boolean).join(" - "), 160)}${c.kind ? ` (${c.kind})` : ""}`);
  const rated = !!(lScale && iScale);
  const none = "(no scale is pinned in this set; state no likelihood and no impact)";
  return {
    vars: {
      context: [jscAiOneLine(context) ? String(context).trim() : "(no description given)",
        compLines.length ? "Components:\n" + compLines.join("\n") : "Components: (none listed)"].join("\n\n"),
      existing: risks.length ? risks.map(r => `- ${jscAiOneLine([r.label, text(r.title)].filter(Boolean).join(": "), 120)} - ${jscAiOneLine(text(r.scenario), 240)}`).join("\n") : "(none)",
      likelihood: rated ? jscAiLevelLines(lScale, text) : none,
      impact: rated ? jscAiLevelLines(iScale, text) : none,
      count: String(count), lang,
    },
    schema: jscAiRiskSchema(rated ? lScale.levels.map(l => l.level) : [], rated ? iScale.levels.map(l => l.level) : []),
    compKeys,
  };
}
/* An answer of the wrong shape is not a suggestion at all: the caller asks
   again. `bad` marks the error for the retry budget. */
function jscAiBadOutput(message) { const e = new Error(message); e.badOutput = true; return e; }
function jscAiRiskShape(answer) {
  if (!answer || typeof answer !== "object" || !Array.isArray(answer.risks)) throw jscAiBadOutput("the answer has no list \"risks\"");
  return answer;
}
/* Checks pass A's answer against what was sent. A draft without a title or
   scenario, or with the title of a risk that exists already (or of an
   earlier draft), is dropped and named. A component key that was not sent
   and a level code the scale does not define are removed from the draft and
   noted on it. Nothing here asks the model again. */
function jscAiRiskCheck(answer, { compKeys, lCodes, iCodes, existingTitles }) {
  const seen = new Set([...existingTitles].map(t => jscAiOneLine(t).toLowerCase()));
  const risks = [], dropped = [];
  for (const r of jscAiRiskShape(answer).risks) {
    const title = jscAiOneLine(r && r.title), scenario = String((r && r.scenario) || "").trim(), notes = [];
    if (!title || !scenario) { dropped.push({ title: title || "(no title)", why: "empty" }); continue; }
    if (seen.has(title.toLowerCase())) { dropped.push({ title, why: "duplicate" }); continue; }
    seen.add(title.toLowerCase());
    const keys = Array.isArray(r.components) ? [...new Set(r.components.map(String))] : [];
    const unknown = keys.filter(k => !compKeys.has(k));
    if (unknown.length) notes.push(`unknown component key removed: ${unknown.join(", ")}`);
    const out = { title, scenario, components: keys.filter(k => compKeys.has(k)).map(k => compKeys.get(k)), reason: jscAiOneLine(r.reason, 600), notes };
    if (lCodes.length && iCodes.length) {
      if (lCodes.includes(r.likelihood) && iCodes.includes(r.impact)) { out.likelihood = r.likelihood; out.impact = r.impact; }
      else notes.push("likelihood or impact is not a code of the scale; the draft carries no rating");
    }
    risks.push(out);
  }
  return { risks, dropped };
}

/* ---------- pass B: suggest treatments ---------- */
const JSC_AI_TREAT_SCHEMA = { type: "object", additionalProperties: false, required: ["treatments"], properties: { treatments: { type: "array",
  items: { type: "object", additionalProperties: false, required: ["requirement", "reason"],
    properties: { requirement: { type: "string" }, reason: { type: "string" } } } } } };

/* The candidate requirements as the text of the prompt's stable part, cut
   into slices of at most `size`. reqs: [{id, label, title, prose}] in a
   stable order. Keys are numbered across the slices, so a key names one
   requirement in the whole run. */
function jscAiCandidates(reqs, size, text) {
  const n = Math.max(1, Number(size) || 400), slices = [];
  for (let at = 0; at < reqs.length; at += n) {
    const keys = new Map(), lines = [];
    reqs.slice(at, at + n).forEach((q, i) => {
      const key = "Q" + (at + i + 1);
      keys.set(key, q.id);
      lines.push(`${key} | ${jscAiOneLine(q.label, 40)} | ${jscAiOneLine(text(q.title), 120)} | ${jscAiOneLine(text(q.prose), 220)}`);
    });
    slices.push({ text: lines.join("\n"), keys });
  }
  return slices;
}
const jscAiRiskText = (r, text) => [jscAiOneLine([r.label, text(r.title)].filter(Boolean).join(": ")), String(text(r.scenario) || "").trim()].filter(Boolean).join("\n");
function jscAiTreatShape(answer) {
  if (!answer || typeof answer !== "object" || !Array.isArray(answer.treatments)) throw jscAiBadOutput("the answer has no list \"treatments\"");
  return answer;
}
/* Checks pass B's answer: a key that was not sent is dropped, a requirement
   the risk names already is dropped, a requirement named twice counts once. */
function jscAiTreatCheck(answer, { keys, already }) {
  const treatments = [], seen = new Set();
  let unknown = 0, known = 0;
  for (const t of jscAiTreatShape(answer).treatments) {
    const id = keys.get(String((t && t.requirement) || "").trim());
    if (!id) { unknown++; continue; }
    if (already.has(id) || seen.has(id)) { known++; continue; }
    seen.add(id);
    treatments.push({ id, reason: jscAiOneLine(t.reason, 400) });
  }
  return { treatments, unknown, known };
}


/* ---------- pass C: draft a check ----------
   One call per rule. What the model may use comes from the kernel schema:
   the page passes the operator and fact-type enums of $defs/checkOp and
   $defs/checkFactType, so prompt, answer schema and kernel cannot disagree.
   The answer is assembled into a Check in code (jascon-checks.js) and judged
   there by the same rules as a check written by hand. */
const JSC_AI_CHECK_OPS = {
  "equals": "equals: the value is exactly expected (one value; decimals compare by value)",
  "one-of": "one-of: the value is one of the listed values (one value)",
  "at-least": "at-least: the value is expected or more (integer or decimal)",
  "at-most": "at-most: the value is expected or less (integer or decimal)",
  "present": "present: the fact was reported",
  "absent": "absent: the fact was not reported (looked for and not found)",
  "includes-all": "includes-all: the list contains every listed value",
  "excludes-all": "excludes-all: the list contains none of the listed values",
  "subset-of": "subset-of: every element of the list is one of the listed values; [] means the list must be empty",
  "matches": "matches: the whole value matches the pattern; on a list, every element does",
  "matches-not": "matches-not: the whole value does not match the pattern; on a list, no element does",
};
function jscAiCheckOps(ops) {
  return ops.map(op => { if (!JSC_AI_CHECK_OPS[op]) throw new Error(`no description for the operator ${op}`); return "- " + JSC_AI_CHECK_OPS[op]; }).join("\n");
}
function jscAiCheckSchema(ops, types) {
  const assertion = { type: "object", additionalProperties: false, required: ["fact", "op", "expected"],
    properties: { fact: { type: "string" }, op: { type: "string", enum: [...ops] }, expected: { type: "string" } } };
  return { type: "object", additionalProperties: false, required: ["fits", "reason", "each", "facts", "criteria", "applies_when", "collector"],
    properties: { fits: { type: "boolean" }, reason: { type: "string" }, each: { type: "string" },
      facts: { type: "array", items: { type: "object", additionalProperties: false, required: ["name", "type", "cardinality", "description"],
        properties: { name: { type: "string" }, type: { type: "string", enum: [...types] }, cardinality: { type: "string", enum: ["one", "many"] },
          description: { type: "string" } } } },
      criteria: { type: "array", items: assertion }, applies_when: { type: "array", items: assertion }, collector: { type: "string" } } };
}
/* The RULE block: the varying item, last in the prompt. params: Map name ->
   {statement, decl} (jscChecksParams); text: a language-map reader. */
function jscAiCheckRule({ req, statementIds, params, audit, remediation, description, text }) {
  const cover = new Set(statementIds && statementIds.length ? statementIds : (req.statements || []).map(s => s.id));
  const lines = [`title: ${jscAiOneLine([req.label, text(req.title)].filter(Boolean).join(": "))}`];
  for (const s of req.statements || []) if (cover.has(s.id)) lines.push(`clause ${s.id} (${s.modality}): ${jscAiOneLine(text(s.prose))}`);
  const ps = [...params].map(([name, { decl }]) => `${name} (${[decl.type, decl.tightening && "tightening " + decl.tightening,
    decl.min !== undefined && "min " + decl.min, decl.max !== undefined && "max " + decl.max,
    decl.choices && "choices " + decl.choices.map(c => c.value).join("|")].filter(Boolean).join(", ")})`);
  lines.push(`parameters: ${ps.length ? ps.join("; ") : "none"}`);
  if (String(audit || "").trim()) lines.push(`audit:\n${String(audit).trim()}`);
  if (String(remediation || "").trim()) lines.push(`remediation (what a compliant system looks like):\n${String(remediation).trim()}`);
  if (String(description || "").trim()) lines.push(`description of the check:\n${String(description).trim()}`);
  return lines.join("\n");
}
function jscAiCheckShape(answer) {
  if (!answer || typeof answer !== "object" || typeof answer.fits !== "boolean") throw jscAiBadOutput("the answer has no \"fits\"");
  for (const k of ["facts", "criteria", "applies_when"]) if (!Array.isArray(answer[k])) throw jscAiBadOutput(`the answer has no list "${k}"`);
  return answer;
}

/* Size of a run before it is paid for. A token is taken as four characters,
   which is rough for English and low for German; the figure is an order of
   magnitude, and the log shows what the service counted beside it. */
function jscAiEstimate(prompts) {
  const chars = prompts.reduce((s, p) => s + p.length, 0);
  return { calls: prompts.length, chars, tokens: Math.ceil(chars / 4) };
}

/* ====================================================================
   The call layer. `state` and `l` are the only names the core block takes
   from outside: the cancel flag and the log.
   ==================================================================== */
const jscAiCore = (() => {
const state = { cancel: false };
const quiet = () => {};
const l = typeof jscLog !== "undefined" ? jscLog : { info: quiet, ok: quiet, warn: quiet, err: quiet, debug: quiet };

// ===== core (DOM-free) =====
// Models that still accept thinkingLevel "minimal". Newer models dropped it: keep this an allowlist.
const MINIMAL_OK = new Set(["gemini-3.6-flash", "gemini-3.5-flash-lite"]);
function clampLevel(model, level) {
  if (level === "minimal" && !MINIMAL_OK.has(model)) {
    l.info(`${model} has no "minimal" thinking level; using "low"`);
    return "low";
  }
  return level;
}

const MAX_HOPS = 3;             // three hops of 32K thinking and output; a call that needs more is too big
const HOP_TIMEOUT_MS = 600000;  // the service closes a non-streaming connection after ten minutes
const MAX_RETRIES = 5;          // ceiling for every reason to ask again; the setting can only go lower

function apiError(status, message) {
  const e = new Error(String(message).replace(/\s+/g, " ").trim().slice(0, 400));
  e.status = status;
  return e;
}
/* Worth another attempt: rate limit, server error, a dropped connection, the
   ten-minute wall, and an answer of the wrong shape. Everything else raises
   at once. */
function isTransient(e) {
  if (e.badOutput) return true;
  if (typeof e.status === "number") return e.status === 429 || e.status >= 500;
  return e instanceof TypeError || e.name === "TimeoutError";   // fetch rejects with a TypeError when the network fails
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* Gemini, native. The loop continues a call the service cut at its per-hop
   ceiling (finishReason CONTINUATION, or MAX_TOKENS with a token): the same
   body again with the token, never the partial output. Models that never
   continue leave the loop after one pass. */
async function geminiOnce(prompt, cfg) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(cfg.model)}:generateContent`;
  const body = {
    contents: [{ role: "user", parts: [{ text: prompt }] }],
    generationConfig: {
      responseMimeType: "application/json",
      responseJsonSchema: cfg.schema,
      thinkingConfig: { thinkingLevel: clampLevel(cfg.model, cfg.level) },
    },
  };
  let text = "", token = null;
  for (let hop = 1; hop <= MAX_HOPS; hop++) {
    const req = token
      ? { ...body, continuationToken: token, generationConfig: { ...body.generationConfig, maxOutputTokens: 32768 * hop } }
      : body;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": cfg.apiKey },   // in the header, never in the URL
      body: JSON.stringify(req),
      signal: AbortSignal.timeout(HOP_TIMEOUT_MS),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.error) throw apiError(res.status, (data.error && data.error.message) || `HTTP ${res.status}`);
    const cand = (data.candidates || [])[0];
    if (!cand) throw apiError(0, `the service returned no answer (${(data.promptFeedback && data.promptFeedback.blockReason) || "no candidate"})`);
    text += ((cand.content && cand.content.parts) || []).map(p => p.text || "").join("");   // "": a hop may resume inside a string
    const u = data.usageMetadata || {};
    l.debug(`hop ${hop}: ${cand.finishReason} · out ${u.candidatesTokenCount ?? "?"} · thought ${u.thoughtsTokenCount ?? "?"} · cached ${u.cachedContentTokenCount ?? 0}`);
    if (cfg.onUsage) cfg.onUsage({ input: u.promptTokenCount || 0, output: u.candidatesTokenCount || 0, thoughts: u.thoughtsTokenCount || 0, cached: u.cachedContentTokenCount || 0 });
    token = cand.continuationToken || null;
    const more = cand.finishReason === "CONTINUATION" || (cand.finishReason === "MAX_TOKENS" && token);
    if (!more) break;
    if (hop === MAX_HOPS) throw apiError(0, `still ${cand.finishReason} after ${MAX_HOPS} hops: send fewer requirements per call or lower the thinking level`);
    l.warn(`hop ${hop} ended with ${cand.finishReason}; continuing`);
  }
  return text;
}

/* The chat-completions form: OpenRouter, and an endpoint of one's own that
   speaks the same protocol (cfg.baseUrl). The thinking level is a Gemini
   control and is not sent here. */
async function chatOnce(prompt, cfg) {
  const own = cfg.backend === "openai";
  const url = own ? `${String(cfg.baseUrl || "").replace(/\/+$/, "")}/chat/completions` : "https://openrouter.ai/api/v1/chat/completions";
  const headers = { "Content-Type": "application/json", "Authorization": `Bearer ${cfg.apiKey}` };
  const body = {
    model: cfg.model,
    messages: [{ role: "user", content: prompt }],
    response_format: { type: "json_schema", json_schema: { name: "result", strict: true, schema: cfg.schema } },
  };
  if (!own) {
    headers["X-Title"] = "JASCON App";
    body.provider = { require_parameters: true };   // route only to providers that honour the schema
  }
  const res = await fetch(url, { method: "POST", headers, body: JSON.stringify(body), signal: AbortSignal.timeout(HOP_TIMEOUT_MS) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    const err = data.error || {};
    throw apiError(Number(err.code) || res.status, err.message || (data.error ? JSON.stringify(data.error) : `HTTP ${res.status}`));
  }
  const choice = (data.choices || [])[0];
  if (!choice) throw apiError(0, "the service returned no answer");
  const u = data.usage || {};
  l.debug(`${choice.finish_reason} · in ${u.prompt_tokens ?? "?"} · out ${u.completion_tokens ?? "?"}`);
  if (cfg.onUsage) cfg.onUsage({ input: u.prompt_tokens || 0, output: u.completion_tokens || 0,
    thoughts: (u.completion_tokens_details && u.completion_tokens_details.reasoning_tokens) || 0,
    cached: (u.prompt_tokens_details && u.prompt_tokens_details.cached_tokens) || 0 });
  return String((choice.message && choice.message.content) ?? "");
}

async function llmOnce(prompt, cfg) {
  return cfg.backend === "gemini" ? geminiOnce(prompt, cfg) : chatOnce(prompt, cfg);
}

const stripFences = s => s.replace(/^\s*```(?:json)?/i, "").replace(/```\s*$/i, "").trim();
function extractJson(text) {
  const trim = String(text).trim();
  try { return JSON.parse(trim); } catch (e) { /* try the next form */ }
  const stripped = stripFences(trim);
  try { return JSON.parse(stripped); } catch (e) { /* try the next form */ }
  const s = stripped.indexOf("{"), e = stripped.lastIndexOf("}");
  if (s >= 0 && e > s) {
    try { return JSON.parse(stripped.slice(s, e + 1)); } catch (err) { /* falls through */ }
  }
  throw new Error("could not extract JSON from response");
}

/* One call with its retry budget. Without `parse` the answer text is
   returned. With it, the parsed and shape-checked answer is; a parse that
   throws an error marked badOutput costs one retry like a transient error. */
async function llm(prompt, cfg, label = "call", parse = null) {
  const retries = Math.min(MAX_RETRIES, Math.max(0, cfg.retries | 0));
  let attempt = 0;
  while (true) {
    if (state.cancel) throw new Error("cancelled");
    try {
      const t0 = performance.now();
      const text = await llmOnce(prompt, cfg);
      l.debug(`${label} ← ${(text.length / 1024).toFixed(1)} kB in ${Math.round(performance.now() - t0)} ms [${cfg.backend}/${cfg.model}]`);
      return parse ? parse(text) : text;
    } catch (e) {
      if (!isTransient(e)) throw e;   // 400, 401, 403, 404: show the reason, do not burn quota
      attempt++;
      if (attempt > retries) throw e;
      const wait = 500 * Math.pow(2, attempt - 1);   // 500, 1000, 2000 ...
      l.warn(`${label} failed (${e.message}); retry ${attempt}/${retries} in ${wait} ms`);
      await sleep(wait);
    }
  }
}

/* Runs `tasks` (functions that return a promise) with at most `limit` in
   flight. One task's error becomes its result and the others go on. After a
   cancel no further task starts; those not started end as {cancelled}. */
async function runPool(tasks, limit, onProgress) {
  const results = new Array(tasks.length);
  let done = 0, next = 0;
  const workers = Array.from({ length: Math.max(1, Math.min(limit | 0 || 1, tasks.length)) }, async () => {
    while (next < tasks.length) {
      const i = next++;
      if (state.cancel) results[i] = { cancelled: true };
      else {
        try { results[i] = await tasks[i](); }
        catch (e) { results[i] = { error: e }; }
      }
      done++;
      if (onProgress) onProgress(done, tasks.length);
    }
  });
  await Promise.all(workers);
  return results;
}
// ===== end core =====

return { state, MINIMAL_OK, MAX_RETRIES, clampLevel, apiError, isTransient, geminiOnce, chatOnce, llmOnce, llm, runPool, extractJson };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_AI_BACKENDS, JSC_AI_LEVELS, JSC_PROMPTS, jscPromptFill, jscPromptMissing, jscAiRiskSchema, jscAiRiskInput,
    jscAiRiskShape, jscAiRiskCheck, JSC_AI_TREAT_SCHEMA, jscAiCandidates, jscAiRiskText, jscAiTreatShape, jscAiTreatCheck,
    jscAiEstimate, jscAiCore, JSC_AI_CHECK_OPS, jscAiCheckOps, jscAiCheckSchema, jscAiCheckRule, jscAiCheckShape };
}

/* ====================================================================
   Browser part: the key in memory, the settings of a call, the answer
   cache, and the two widgets the pages share.
   ==================================================================== */
if (typeof window !== "undefined") (() => {

jscI18n.add("de", {
  "Prompt: suggest risks": "Prompt: Risiken vorschlagen", "Prompt: suggest treatments": "Prompt: Behandlungen vorschlagen",
  "Prompt: draft a check": "Prompt: Prüfung entwerfen",
  "OpenAI-compatible endpoint": "OpenAI-kompatibler Endpunkt",
  "Key": "Schlüssel", "Key for {backend}": "Schlüssel für {backend}", "Forget the key": "Schlüssel vergessen",
  "a key is in memory": "ein Schlüssel liegt im Speicher der Seite", "no key": "kein Schlüssel",
  "model": "Modell", "thinking": "Denkstufe", "(no model chosen)": "(kein Modell gewählt)",
  "The key is held in the memory of this page and of the hub, never in the browser's storage, a set or an export. Reloading the hub clears it. Without a key nothing leaves this browser.":
    "Der Schlüssel liegt im Speicher dieser Seite und des Hubs, nie im Speicher des Browsers, in einem Set oder einem Export. Ein Neuladen des Hubs löscht ihn. Ohne Schlüssel verlässt nichts diesen Browser.",
  "No key for {backend}. Type it in the field above.": "Kein Schlüssel für {backend}. Bitte im Feld oben eingeben.",
  "No model is chosen for {backend}. Choose one in the settings.": "Für {backend} ist kein Modell gewählt. Bitte in den Einstellungen wählen.",
  "No base URL is set for the endpoint. Set one in the settings.": "Für den Endpunkt ist keine Basis-URL gesetzt. Bitte in den Einstellungen setzen.",
  "Reset to default": "Auf Vorgabe zurücksetzen", "edited": "bearbeitet", "default": "Vorgabe",
  "Missing placeholder {ph}: it is appended when the prompt is sent.": "Platzhalter {ph} fehlt: Er wird beim Senden angehängt.",
  "Placeholders: {list}": "Platzhalter: {list}",
  "answer taken from the cache: {label}": "Antwort aus dem Cache: {label}",
});

const PROMPT_PREFIX = "jsc:cfg:prompt:", CACHE_KEY = "jsc:cfg:ai:cache", CACHE_MAX = 80;
const core = jscAiCore;

/* ---------- the key: memory only ----------
   keys[backend] is the only place a key is held in this page. Inside the
   hub the key is also handed to the hub window, which holds it in a
   variable of its own and gives it back to the next tool page. */
const keys = Object.create(null), keyListeners = [];
const embedded = window.parent !== window;
const local = location.protocol === "file:";
const toParent = msg => { if (embedded) window.parent.postMessage({ jsc: "ai-key", ...msg }, local ? "*" : location.origin); };
window.addEventListener("message", e => {
  if (!embedded || e.source !== window.parent || (!local && e.origin !== location.origin)) return;
  const d = e.data;
  if (!d || d.jsc !== "ai-key" || d.op !== "keys" || !d.keys || typeof d.keys !== "object") return;
  /* the hub's state replaces this page's: a key the hub forgot is forgotten here too */
  for (const b of Object.keys(JSC_AI_BACKENDS)) { if (typeof d.keys[b] === "string" && d.keys[b]) keys[b] = d.keys[b]; else delete keys[b]; }
  keyListeners.forEach(f => f());
});
toParent({ op: "get" });

const num = (key, min, max, def) => { const n = parseInt(jscCfg.get(key), 10); return Number.isFinite(n) ? Math.max(min, Math.min(max, n)) : def; };

const jscAi = {
  core,
  backend() { const b = jscCfg.get("ai:backend"); return JSC_AI_BACKENDS[b] ? b : "gemini"; },
  label(backend) { return T(JSC_AI_BACKENDS[backend || this.backend()].label); },
  model() { return jscCfg.get("ai:model:" + this.backend()).trim(); },
  level() { const v = jscCfg.get("ai:thinking"); return JSC_AI_LEVELS.includes(v) ? v : "medium"; },
  concurrency() { return num("ai:concurrency", 1, 8, 3); },
  chunk() { return num("ai:chunk", 20, 2000, 400); },
  key() { return keys[this.backend()] || ""; },
  setKey(value) {
    const b = this.backend(), v = String(value || "").trim();
    if (v) keys[b] = v; else delete keys[b];
    toParent({ op: "set", backend: b, key: v });
    keyListeners.forEach(f => f());
  },
  /* What is missing before a call can be made, as a sentence; "" when
     nothing is. A configuration fault is told before the run, not retried. */
  missing() {
    const b = this.backend();
    if (!this.model()) return T("No model is chosen for {backend}. Choose one in the settings.", { backend: this.label() });
    if (b === "openai" && !/^https?:\/\/./.test(jscCfg.get("ai:base:openai").trim())) return T("No base URL is set for the endpoint. Set one in the settings.");
    if (!this.key()) return T("No key for {backend}. Type it in the field above.", { backend: this.label() });
    return "";
  },
  /* The settings of one call, read once per run. */
  cfgFor(schema) {
    const why = this.missing();
    if (why) throw new Error(why);
    const b = this.backend();
    return { backend: b, model: this.model(), level: this.level(), apiKey: this.key(), schema, retries: num("ai:retries", 0, core.MAX_RETRIES, 2),
      baseUrl: jscCfg.get("ai:base:openai").trim(), onUsage: u => { for (const k of Object.keys(u)) this.usage[k] += u[k]; this.usage.calls++; } };
  },
  usage: { calls: 0, input: 0, output: 0, thoughts: 0, cached: 0 },
  resetUsage() { for (const k of Object.keys(this.usage)) this.usage[k] = 0; },
  cancel() { core.state.cancel = true; },
  resetCancel() { core.state.cancel = false; },

  /* ---------- prompts ---------- */
  prompt(key) {
    const own = localStorage.getItem(PROMPT_PREFIX + key);
    return own !== null && own.trim() ? own : JSC_PROMPTS.find(p => p.key === key).def;
  },
  fill(key, vars) { return jscPromptFill(key, this.prompt(key), vars).text; },

  /* ---------- answer cache ----------
     The same question to the same model is paid for once. The key is a hash
     over everything that shapes the answer (service, model, thinking level,
     schema, prompt), so a changed prompt or a changed set asks anew and a
     stale answer is never reused. Kept in localStorage; it holds answers,
     never a key. A cache fault never stops a run. */
  async cacheId(cfg, prompt) { return jscSha256(JSON.stringify([cfg.backend, cfg.model, cfg.level, cfg.schema, prompt])); },
  cacheRead() { try { return JSON.parse(localStorage.getItem(CACHE_KEY)) || {}; } catch (e) { return {}; } },
  cacheWrite(id, answer) {
    try {
      const all = this.cacheRead();
      all[id] = { a: answer, t: Date.now() };
      const ids = Object.keys(all).sort((x, y) => all[x].t - all[y].t);
      while (ids.length > CACHE_MAX) delete all[ids.shift()];
      localStorage.setItem(CACHE_KEY, JSON.stringify(all));
    } catch (e) { jscLog.warn("answer cache: " + e.message); }
  },
  /* One question. `shape` throws jscAiBadOutput for an answer that is not
     what was asked for. Returns {answer, cached}. */
  async ask(prompt, cfg, label, shape, fresh) {
    const id = await this.cacheId(cfg, prompt), hit = fresh ? null : this.cacheRead()[id];
    if (hit) { jscLog.debug(T("answer taken from the cache: {label}", { label })); return { answer: hit.a, cached: true }; }
    jscLog.info(`→ ${label} · ${cfg.backend}/${cfg.model} · ${(prompt.length / 1024).toFixed(1)} kB`);
    const answer = await core.llm(prompt, cfg, label, text => shape(core.extractJson(text)));
    this.cacheWrite(id, answer);
    return { answer, cached: false };
  },

  /* ---------- widgets ---------- */
  /* Which service and model a call goes to, and the field for its key. */
  accessPanel(host) {
    const render = () => {
      const b = this.backend(), has = !!this.key();
      host.innerHTML = `<div class="wbrow"><span class="chip"><b>${jscEsc(this.label())}</b>${jscEsc(T("model"))} ${jscEsc(this.model() || T("(no model chosen)"))}${b === "gemini" ? ` · ${jscEsc(T("thinking"))} ${jscEsc(this.level())}` : ""}</span>
        <label for="ai-key">${jscEsc(T("Key"))}</label><input type="password" id="ai-key" class="ai-key" autocomplete="off" spellcheck="false" style="min-width:260px" aria-label="${jscEsc(T("Key for {backend}", { backend: this.label() }))}">
        <span class="${has ? "verdict-ok" : "hint"}" role="status">${jscEsc(T(has ? "a key is in memory" : "no key"))}</span>
        <button type="button" class="small ai-forget" ${has ? "" : "disabled"}>${jscEsc(T("Forget the key"))}</button>
        <a class="btn small" href="config.html" target="_blank" rel="noopener">${jscEsc(T("Settings"))}</a></div>
        <p class="hint" style="max-width:86ch">${jscEsc(T("The key is held in the memory of this page and of the hub, never in the browser's storage, a set or an export. Reloading the hub clears it. Without a key nothing leaves this browser."))}</p>`;
      host.querySelector(".ai-key").addEventListener("change", e => this.setKey(e.target.value));
      host.querySelector(".ai-forget").addEventListener("click", () => this.setKey(""));
    };
    keyListeners.push(render);
    window.addEventListener("storage", e => { if (e.key && e.key.startsWith("jsc:cfg:ai:") && e.key !== CACHE_KEY) keyListeners.forEach(f => f()); });
    render();
  },
  onKey(fn) { keyListeners.push(fn); },
  /* The editor of one prompt: the text in use, a reset to the default, and a
     warning while a needed placeholder is missing. Saved as it is typed. */
  promptEditor(host, key) {
    const p = JSC_PROMPTS.find(x => x.key === key), id = "prompt-" + key;
    host.innerHTML = `<div class="wbrow" style="margin-bottom:4px"><label class="nano" for="${id}">${jscEsc(T(p.label))}</label><span class="hint ai-state"></span><div style="flex:1"></div>
        <button type="button" class="small ai-reset">${jscEsc(T("Reset to default"))}</button></div>
      <textarea id="${id}" spellcheck="false" style="width:100%;min-height:200px;resize:vertical;font-family:var(--mono);font-size:12px"></textarea>
      <div class="hint">${jscEsc(T("Placeholders: {list}", { list: [...p.need, ...p.also].join(" ") }))}</div><div class="verdict-warn ai-missing" role="status"></div>`;
    const area = host.querySelector("textarea"), stateEl = host.querySelector(".ai-state"), missing = host.querySelector(".ai-missing");
    const show = () => {
      stateEl.textContent = T(area.value === p.def ? "default" : "edited");
      missing.textContent = jscPromptMissing(key, area.value).map(ph => T("Missing placeholder {ph}: it is appended when the prompt is sent.", { ph })).join(" ");
    };
    area.value = this.prompt(key);
    area.addEventListener("input", () => {
      if (area.value === p.def || !area.value.trim()) localStorage.removeItem(PROMPT_PREFIX + key); else localStorage.setItem(PROMPT_PREFIX + key, area.value);
      show();
      host.dispatchEvent(new CustomEvent("jsc:prompt"));
    });
    host.querySelector(".ai-reset").addEventListener("click", () => { localStorage.removeItem(PROMPT_PREFIX + key); area.value = p.def; show(); host.dispatchEvent(new CustomEvent("jsc:prompt")); });
    show();
  },
};
window.jscAi = jscAi;

})();
