/* JASCON-App: what the Checks tool computes, without the page.

   The Check type (drafts/CP-CHECK-1.md, kernel 2.0.0) splits a machine check in
   two: a collector (code that reports facts) and criteria (comparisons that
   decide). This file holds what the tool does around that split, as plain
   functions of plain data, so that tests run it in node:

   - the rules a set offers for checks: requirements that carry
     assessment-criteria@1 (the CIS import puts audit and remediation text
     and the automated/manual marking there), with the checks they have;
   - minting ids and a default platform for a new check;
   - assembling a Check from a model's answer. The model writes facts,
     criteria and collector source; this code mints the id, sets the
     requirement and clauses, and refuses an answer whose "expected" is not
     JSON or that names a parameter the rule does not have. The rules of
     jascon-rules.js (CHECK-1..7) then judge the result like any check;
   - a lint of collector source for commands that change a system. A
     collector must only read; the lint is a list of warnings for a person,
     never a proof that a script is harmless.

   Not here: the page, the model call (jascon-ai.js), running a collector
   (the app cannot and does not), recording a run. */
"use strict";

const jscChecksCore = (typeof module !== "undefined" && module.exports) ? require("./jascon-core.js") : { jscSlug };
const JSC_CHECKS = {
  COLLECTOR: "https://ns.jascon.net/stdlib/facet/collector@1",
  ACRIT: "https://ns.jascon.net/stdlib/facet/assessment-criteria@1",
  /* the hand-over from the Import page: which rules to draft checks for, in which runtime. Not a secret. */
  QUEUE: "jsc:cfg:checks:queue",
  RUNTIMES: ["bash", "sh", "python", "powershell", "ansible", "http-api"],
};

/* ---------- the rules a set offers ----------
   objs: Map(id -> {type, obj}). A requirement is offered when it carries
   assessment-criteria@1 or when a check names it. The payload may be flat or
   keyed by statement; the flat fields win, the first statement's fill gaps.
   -> [{ id, req, method, audit, remediation, checks: [check id] }] by id */
function jscChecksRules(objs) {
  const checksOf = new Map();
  for (const [id, r] of objs) {
    if (r.type !== "check") continue;
    const ref = r.obj["requirement-ref"];
    if (!checksOf.has(ref)) checksOf.set(ref, []);
    checksOf.get(ref).push(id);
  }
  const out = [];
  for (const [id, r] of objs) {
    if (r.type !== "requirement") continue;
    const ac = ((r.obj.facets || {})[JSC_CHECKS.ACRIT]) || null;
    if (!ac && !checksOf.has(id)) continue;
    const first = ac && ac["by-statement"] ? Object.values(ac["by-statement"])[0] || {} : {};
    const pick = k => (ac && ac[k] !== undefined ? ac[k] : first[k]);
    out.push({ id, req: r.obj, method: pick("method") || null, audit: pick("audit") || null, remediation: pick("remediation") || null,
      checks: (checksOf.get(id) || []).sort() });
  }
  return out.sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

/* An id for a new check under the organisation's namespace, unique in the
   set: <ns>/check/<requirement label or last id segment>-<runtime>. */
function jscChecksMintId(ns, req, runtime, taken) {
  const base = `${String(ns).replace(/\/+$/, "")}/check/${jscChecksCore.jscSlug(req.label || String(req.id).split("/").pop())}-${runtime}`;
  let id = base;
  for (let n = 2; taken.has(id); n++) id = `${base}-${n}`;
  return id;
}
/* The platform a requirement's checks run on, by default: the requirement's
   own namespace (everything before /req/) plus /platform. Opaque, like every
   kernel URI; the page lets it be changed. */
function jscChecksPlatform(reqId, fallbackNs) {
  const at = String(reqId).indexOf("/req/");
  return at > 0 ? String(reqId).slice(0, at) + "/platform" : `${String(fallbackNs).replace(/\/+$/, "")}/platform/host`;
}

/* The parameters a check may bind: those declared on the clauses it covers,
   name -> {statement, decl}. A name declared on two clauses is left out:
   CHECK-4 would refuse a binding to it. */
function jscChecksParams(req, statementIds) {
  const cover = new Set(statementIds && statementIds.length ? statementIds : (req.statements || []).map(s => s.id));
  const seen = new Map(), twice = new Set();
  for (const s of req.statements || []) {
    if (!cover.has(s.id)) continue;
    for (const p of s.parameters || []) { if (seen.has(p.name)) twice.add(p.name); else seen.set(p.name, { statement: s.id, decl: p }); }
  }
  for (const n of twice) seen.delete(n);
  return seen;
}

/* ---------- a model's answer -> a Check ----------
   answer: the shape of jscAiCheckSchema (jascon-ai.js). ctx: { req, statementIds,
   platform, runtime, id, authorRef, date, lang, drafter, derivedFrom? }.
   -> { fits, reason, check: object or null, problems: [string] }
   A problem means no check was assembled; the reason is shown. */
function jscChecksFromAnswer(answer, ctx) {
  const problems = [], reason = String((answer && answer.reason) || "").trim();
  if (!answer || answer.fits !== true) return { fits: false, reason, check: null, problems };
  const params = jscChecksParams(ctx.req, ctx.statementIds);
  const assertions = (list, where) => (list || []).map((a, i) => {
    const out = { fact: String(a.fact || ""), op: String(a.op || "") };
    const text = String(a.expected === undefined || a.expected === null ? "" : a.expected).trim();
    if (out.op === "present" || out.op === "absent") return out;
    if (!text) { problems.push(`${where}[${i}]: ${out.op} needs a value and the answer gives none`); return out; }
    let v;
    try { v = JSON.parse(text); } catch (e) { problems.push(`${where}[${i}]: expected is not JSON: ${text.slice(0, 80)}`); return out; }
    if (v && typeof v === "object" && !Array.isArray(v)) {
      if (typeof v.param !== "string" || Object.keys(v).length !== 1) { problems.push(`${where}[${i}]: an object is allowed only as {"param": name}`); return out; }
      if (!params.has(v.param)) { problems.push(`${where}[${i}]: parameter '${v.param}' was not sent; the rule has ${params.size ? [...params.keys()].join(", ") : "no parameter"}`); return out; }
    }
    if (typeof v === "number" && !Number.isInteger(v)) { problems.push(`${where}[${i}]: ${text} is a JSON float; a decimal is written as a string`); return out; }
    out.expected = v;
    return out;
  });
  const criteria = assertions(answer.criteria, "criteria"), appliesWhen = assertions(answer.applies_when, "applies_when");
  const source = String(answer.collector || "").trim();
  if (!criteria.length) problems.push("the answer has no criteria");
  if (!(answer.facts || []).length) problems.push("the answer declares no fact");
  if (!source) problems.push("the answer has no collector source");
  if (problems.length) return { fits: true, reason, check: null, problems };
  const text = v => ({ [ctx.lang]: v });
  const check = { id: ctx.id, version: "0.1.0", lifecycle: "draft",
    title: text(`${ctx.req.label || String(ctx.req.id).split("/").pop()}: ${ctx.runtime} check`),
    "requirement-ref": ctx.req.id };
  if (ctx.statementIds && ctx.statementIds.length) check["statement-ids"] = [...ctx.statementIds];
  check.platform = ctx.platform;
  check.observes = answer.facts.map(f => {
    const d = { name: String(f.name), type: String(f.type) };
    if (f.cardinality === "many") d.cardinality = "many";
    if (String(f.description || "").trim()) d.description = text(String(f.description).trim());
    return d;
  });
  check.criteria = criteria;
  if (appliesWhen.length) check["applies-when"] = appliesWhen;
  if (String(answer.each || "").trim()) check.each = { resource: String(answer.each).trim(), "allow-empty": false };
  check.confidence = "draft";
  check.provenance = { "author-ref": ctx.authorRef, date: ctx.date };
  if (ctx.derivedFrom) check.provenance["derived-from"] = [ctx.derivedFrom];
  check.facets = { [JSC_CHECKS.COLLECTOR]: { collectors: [{ id: ctx.runtime, runtime: ctx.runtime, source: source + "\n" }] } };
  check.annotations = { "jascon-app": { "drafted-by": "model", by: ctx.drafter, on: ctx.date } };
  return { fits: true, reason, check, problems };
}

/* ---------- read-only lint ----------
   A collector reads; it never changes the system it looks at. These
   patterns find the usual ways a script writes, installs, restarts or
   reaches the network. A hit is a warning for the person who reviews the
   check; no hit proves nothing. -> [{ line, text, why }] */
const JSC_LINT = {
  shell: [
    [/(^|[^0-9&<>|])>>?\s*(?!&|\/dev\/null\b)[^\s|;&)]/, "writes to a file (redirection)"],
    [/\b(rm|rmdir|mv|cp|dd|truncate|shred|tee|install|ln|touch|mkdir|mkfs(\.\w+)?|chmod|chown|chgrp|chattr|setfacl)\b/, "changes files"],
    [/\bsed\s+(-\w*i|--in-place)/, "edits a file in place"],
    [/\b(useradd|usermod|userdel|groupadd|groupmod|groupdel|passwd|chpasswd|chage|gpasswd)\b/, "changes accounts"],
    [/\b(systemctl\s+(start|stop|restart|reload|enable|disable|mask|unmask|daemon-reload|set-\w+|kill|isolate)|service\s+\S+\s+(start|stop|restart|reload)|kill|pkill|killall|reboot|shutdown|poweroff|halt|init\s+[0-6])\b/, "changes running services or the machine"],
    [/\b(apt|apt-get|dpkg\s+-[iPr]|dnf|yum|zypper|snap|pip3?|npm|gem)\s+(install|remove|purge|upgrade|update|erase)\b|\bdpkg\s+-(i|r|P)\b/, "installs or removes software"],
    [/\b(sysctl\s+(-w|-p|\S+=)|modprobe|rmmod|insmod|mount|umount|swapon|swapoff|iptables|ip6tables|nft|ufw|firewall-cmd|setenforce|crontab|augtool|update-\w+)\b/, "changes system settings"],
    [/\b(curl|wget|nc|ncat|ssh|scp|rsync|ftp)\b/, "reaches the network"],
  ],
  python: [
    [/\bopen\([^)]*,\s*['"][^'"]*[wax+]/, "writes to a file"],
    [/\b(os\.(remove|unlink|rmdir|rename|replace|chmod|chown|makedirs|mkdir|system)|shutil\.(rmtree|move|copy\w*))\b/, "changes files or runs a shell"],
    [/\b(requests|urllib|http\.client|socket)\b/, "reaches the network"],
  ],
  powershell: [
    [/\b(Set|New|Remove|Stop|Start|Restart|Enable|Disable|Install|Uninstall|Add|Clear|Rename|Move|Copy|Register|Unregister)-[A-Z]\w+/, "a cmdlet that changes state"],
    [/\b(Out-File|Set-Content|Add-Content)\b|(^|[^0-9&])>>?\s*(?!\$null)\S/, "writes to a file"],
    [/\b(Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b/, "reaches the network"],
  ],
  ansible: [
    [/^\s*-?\s*(ansible\.builtin\.)?(copy|template|lineinfile|blockinfile|replace|file|apt|yum|dnf|package|pip|service|systemd|user|group|sysctl|mount|cron|authorized_key|unarchive|get_url|uri|reboot)\s*:/, "a module that changes state"],
    [/^\s*-?\s*(ansible\.builtin\.)?(shell|command|raw|script)\s*:/, "runs a command: check that it only reads"],
  ],
  "http-api": [
    [/\b(POST|PUT|PATCH|DELETE)\b/, "a request that changes state"],
  ],
};
function jscCollectorLint(runtime, source) {
  const rules = JSC_LINT[runtime === "bash" || runtime === "sh" ? "shell" : runtime] || [];
  const out = [];
  String(source || "").split("\n").forEach((line, i) => {
    const code = runtime === "python" || runtime === "bash" || runtime === "sh" || runtime === "powershell" ? line.replace(/(^|\s)#.*$/, "") : line;
    if (!code.trim()) return;
    for (const [re, why] of rules) if (re.test(code)) out.push({ line: i + 1, text: line.trim().slice(0, 120), why });
  });
  return out;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_CHECKS, JSC_LINT, jscChecksRules, jscChecksMintId, jscChecksPlatform, jscChecksParams, jscChecksFromAnswer, jscCollectorLint };
}
