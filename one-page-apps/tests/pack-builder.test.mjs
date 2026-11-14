/* Drives one-page-apps/jascon-pack-builder.html in a real browser and holds
   what it writes to the app's import and to the Python reference.

   1. The worked advice pack, typed into the form from nothing and signed with
      the public fixture key, comes out with the worked pack's Component byte
      for byte and its manifest equal but for the provenance line; the app's
      own import code reads the ZIP as "import" with the publisher proven, and
      validate_core.py (where Python with jsonschema is present) reports the
      signature VERIFIED.
   2. An opened pack keeps its manifest while nothing changes; changed content
      under the opened release, or a changed Component under its old version,
      is refused; with both versions raised the release is ready.
   3. With a catalogue loaded, a suggested value the covered clauses do not
      declare is refused (ADVICE-6).
   5. An OSCAL component definition imported without a catalogue: control
      ids by the NIST rule, statements to clauses, values to suggestions,
      a prefix asked for the other source; what a pack cannot carry named.
   6. The same with the SP 800-53 catalogue loaded: values set for the
      whole control implementation placed, a Rev 4 parameter id renamed to
      the catalogue's, and every clause and value passes ADVICE-5/6.
   4. Signing elsewhere: the prepared bytes signed by openssl (where present)
      make the publisher proven, and a change afterwards asks for a new
      signature.
   Throughout: no script error, and nothing like a key in the stored draft.

   The key is the corpus FIXTURE key of conformance/dsse-vectors.json, whose
   seed is public. Needs Playwright with Chromium; where that is missing the
   test is skipped and says so. */
import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const require = createRequire(import.meta.url);
const core = require("../../jascon-app/jascon-core.js");
const rules = require("../../jascon-app/jascon-rules.js");
let chromium = null;
try { ({ chromium } = require("playwright")); } catch (e) { /* skipped below */ }
const SKIP = !chromium && "Playwright with Chromium is not installed";

const PAGE = pathToFileURL(path.join(ROOT, "one-page-apps/jascon-pack-builder.html")).href;
const WORKED = path.join(ROOT, "jascon/example-packs/dbvendor-server-7-advice");
const VENDOR = "https://dbvendor.example/party/vendor";
const SEED = crypto.createHash("sha256").update("jascon dsse fixture key 1").digest();
const FIXTURE_PUB = JSON.parse(fs.readFileSync(path.join(ROOT, "jascon/conformance/advice-vectors.json"), "utf8"))["fixture-public-key"];
const PEM = "-----BEGIN PRIVATE KEY-----\n" + Buffer.concat([Buffer.from("302e020100300506032b657004220420", "hex"), SEED]).toString("base64") + "\n-----END PRIVATE KEY-----\n";
const KONF = "https://ns.bsi.bund.de/gspp/req/KONF.14.1";

async function open() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "pack-builder-"));
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ acceptDownloads: true, viewport: { width: 1400, height: 1000 } })).newPage();
  const errors = [];
  page.on("pageerror", e => errors.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error") errors.push("console: " + m.text()); });
  /* confirm() is answered yes; prompt() takes the next answer a test queued, or its default */
  const answers = [], prompts = [];
  page.on("dialog", d => { if (d.type() === "prompt") { prompts.push(d.message()); return d.accept(answers.length ? answers.shift() : d.defaultValue()); } return d.accept(); });
  await page.goto(PAGE);
  await page.locator('body[data-state="ready"] #sec-check .status').waitFor();
  const set = async (sel, value) => { const l = page.locator(sel).first(); await settle(); await l.fill(value); await l.dispatchEvent("change"); };
  /* the page says when the panel shows the verdict for everything done so far (body[data-state]) */
  const settle = async () => page.locator('body[data-state="ready"]').waitFor();
  const status = async () => { await settle(); return (await page.locator("#sec-check").innerText()).replace(/\s+/g, " "); };
  const download = async click => {
    const [d] = await Promise.all([page.waitForEvent("download"), page.click(click)]);
    const file = path.join(tmp, d.suggestedFilename());
    await d.saveAs(file);
    return file;
  };
  /* what every test holds at its end */
  const finish = async () => {
    const stored = await page.evaluate(() => localStorage.getItem("jascon-pack-builder:draft:v1") || "");
    assert.doesNotMatch(stored, /PRIVATE KEY|"sig"|sigText|"pub"/, "the stored draft holds no key and no signature");
    assert.deepEqual(errors, [], "no script error on the page");
  };
  const shutdown = async () => { await browser.close(); fs.rmSync(tmp, { recursive: true, force: true }); };
  return { page, tmp, set, settle, status, download, finish, shutdown, answers, prompts };
}
/* The browser is closed whether the test passes or fails; a browser left
   open keeps node waiting after a failed assertion. */
async function withBuilder(fn) {
  const B = await open();
  try { await fn(B); await B.finish(); } finally { await B.shutdown(); }
}
const OPTS = { skip: SKIP, timeout: 120000 };
const unzip = async file => (await core.jscUnzip(fs.readFileSync(file))).map(f => ({ path: f.path.split("/").slice(1).join("/"), text: f.text }));

test("the worked pack, typed in and signed, is the worked pack; the app's import reads it as proven; the reference verifies the signature", OPTS, () => withBuilder(async B => {
  const { page, set } = B;
  await set('[data-bind="origin"]', "https://dbvendor.example");
  /* the publisher is a party, and the page names none: an origin typed does not make one (backlog #70) */
  assert.equal(await page.locator('[data-bind="publisher.ref"]').inputValue(), "", "the origin does not fill in a publisher nobody named");
  assert.match(await B.status(), /Publisher id is empty\. A pack names the party that publishes it, under your origin \(ADVICE-2\); this page does not supply one\./);
  await set('[data-bind="publisher.ref"]', "https://dbvendor.example/party/vendor");
  assert.doesNotMatch(await B.status(), /Publisher id is empty/);
  /* a publisher that was typed still moves with the origin, as every identifier under it does */
  await set('[data-bind="origin"]', "https://db.example");
  assert.equal(await page.locator('[data-bind="publisher.ref"]').inputValue(), "https://db.example/party/vendor");
  await set('[data-bind="origin"]', "https://dbvendor.example");
  assert.equal(await page.locator('[data-bind="publisher.ref"]').inputValue(), VENDOR);
  await set('[data-bind="pack.id"]', "https://dbvendor.example/pack/server-7-hardening");
  await set('[data-bind="pack.version"]', "3");
  await set('[data-bind="pack.title"][data-lang="en"]', "Server 7 hardening advice");
  await set('[data-bind="publisher.name"][data-lang="en"]', "Example DB Vendor Inc.");
  await set('[data-bind="c.0.label"]', "Example DB Server 7");
  await set('[data-bind="c.0.id"]', "https://dbvendor.example/component/server-7");
  await set('[data-bind="c.0.version"]', "2026-10");
  await set('[data-bind="c.0.productVersion"]', "7");
  await set('[data-bind="c.0.title"][data-lang="en"]', "Example DB Server, release line 7");
  const caps = [
    ["cap-tls", KONF, "s1", "Set net.tls.mode to requireTLS and net.tls.disabledProtocols to TLS1_0,TLS1_1,TLS1_2. Clients older than driver 4.2 cannot connect afterwards.", '{"transport-crypto": "tls13"}'],
    ["cap-key-rotation", KONF, "s2", "Rotate the server certificate and key with the rotateCertificates command; no restart is needed. The vendor suggests an interval of 90 days.", ""],
    ["cap-audit-log", "https://ns.nist.gov/sp800-53/req/AU-12", "", "Turn on the audit log with auditLog.destination: file and ship it off the host.", ""],
  ];
  for (const [j, [id, req, clauses, text, bindings]] of caps.entries()) {
    if (j) await page.click('[data-act="add-cap"][data-c="0"]');
    const at = `c.0.k.${j}`;
    await set(`[data-bind="${at}.requirementRef"]`, req);
    await set(`[data-bind="${at}.id"]`, id);
    if (clauses) await set(`[data-bind="${at}.statementIds"]`, clauses);
    await set(`[data-bind="${at}.description"][data-lang="en"]`, text);
    if (bindings) await set(`[data-bindings="${at}"]`, bindings);
  }
  assert.match(await B.status(), /Ready to publish.*claimed/, "unsigned, the publisher is claimed");
  await page.check('input[name="sign-mode"][value="here"]');
  fs.writeFileSync(path.join(B.tmp, "key.pem"), PEM);
  await page.setInputFiles("#pick-key", path.join(B.tmp, "key.pem"));
  assert.match(await B.status(), /Ready to publish.*would import it.*proven/);
  assert.equal((await page.locator("#pubkey").innerText()).trim(), FIXTURE_PUB, "the public key read from the key file");

  const zip = await B.download("#btn-download");
  assert.equal(path.basename(zip), "server-7-hardening-3.zip");
  const files = await unzip(zip);
  assert.deepEqual(files.map(f => f.path).sort(), ["attestation-server-7-hardening.dsse", "attestation-server-7-hardening.json",
    "content-manifest.json", "objects/component/server-7.json"]);
  const get = p => files.find(f => f.path === p).text;
  assert.equal(get("objects/component/server-7.json"), fs.readFileSync(path.join(WORKED, "objects/component/server-7.json"), "utf8"),
    "the Component is the worked pack's, byte for byte");
  const mine = JSON.parse(get("content-manifest.json")), worked = JSON.parse(fs.readFileSync(path.join(WORKED, "content-manifest.json"), "utf8"));
  delete mine.provenance; delete worked.provenance;
  assert.deepEqual(mine, worked, "the manifest is the worked pack's but for its provenance");

  /* the app's import, in node: the same code the hub runs */
  const pack = await rules.jscAdvicePack(files);
  assert.deepEqual(pack.problems, []);
  const plan = await rules.jscAdviceImport(core.jscGraphFrom([]), pack, { trusted: { [VENDOR]: FIXTURE_PUB } });
  assert.equal(plan.result, "import");
  assert.equal(plan.label, "proven");
  const keys = JSON.parse(fs.readFileSync(await B.download("#btn-trusted"), "utf8"));
  assert.deepEqual(keys, { [VENDOR]: FIXTURE_PUB }, "the trusted key file names the publisher and its key");

  /* the reference, where it can run */
  if (spawnSync("python3", ["-c", "import jsonschema"]).status === 0) {
    const dir = path.join(B.tmp, "pack");
    for (const f of files) { fs.mkdirSync(path.dirname(path.join(dir, f.path)), { recursive: true }); fs.writeFileSync(path.join(dir, f.path), f.text); }
    fs.writeFileSync(path.join(B.tmp, "keys.json"), JSON.stringify(keys));
    const run = spawnSync("python3", [path.join(ROOT, "jascon/scripts/validate_core.py"), dir, "--trusted-keys", path.join(B.tmp, "keys.json")], { encoding: "utf8" });
    assert.equal(run.status, 0, run.stdout.slice(-2000));
    assert.match(run.stdout, /pack: https:\/\/dbvendor\.example\/pack\/server-7-hardening release 3 by .* = publisher PROVEN \[attestation binds the manifest \+ signature VERIFIED\]/);
  }
}));

test("an opened pack keeps its manifest until it changes; changed content needs a new release and a new Component version", OPTS, () => withBuilder(async B => {
  const { page, set } = B;
  await page.setInputFiles("#pick-open-folder", WORKED);
  const worked = crypto.createHash("sha256").update(fs.readFileSync(path.join(WORKED, "content-manifest.json"))).digest("hex");
  const opened = await B.status();
  assert.match(opened, /Unchanged from release 3/);
  assert.ok(opened.includes(worked), "an unchanged pack keeps the manifest it was opened with");
  await set('[data-bind="c.0.k.1.description"][data-lang="en"]', "Rotate the certificate every 90 days with rotateCertificates.");
  const changedText = await B.status();
  assert.match(changedText, /RELEASE.*still '3'/);
  assert.match(changedText, /VERSION.*keeps version '2026-10'/);
  assert.match(changedText, /would import it/, "the builder refuses what the app's import would still take");
  await set('[data-bind="pack.version"]', "4");
  assert.match(await B.status(), /VERSION/);
  await set('[data-bind="c.0.version"]', "2026-11");
  assert.match(await B.status(), /Ready to publish/);
  assert.equal(await page.locator("#btn-download").isDisabled(), false);
}));

test("with the catalogue loaded, a suggested value the covered clauses do not declare is refused (ADVICE-6)", OPTS, () => withBuilder(async B => {
  const { page, set } = B;
  await page.setInputFiles("#pick-open-folder", WORKED);
  await page.setInputFiles("#pick-cat-folder", path.join(ROOT, "jascon/examples"));
  await B.settle();
  assert.match(await page.locator("#cat-state").innerText(), /^4 requirement\(s\)/);
  /* the clauses of KONF.14.1 are offered as a list, its parameter with its declared choices */
  const tls = page.locator('[data-cap="c.0.k.0"]');
  assert.equal(await tls.locator("input[data-stmt]").count(), 2);
  assert.match(await tls.locator(".param").innerText(), /transport-crypto[\s\S]*in the declared space/);
  await set('[data-bind="pack.version"]', "4");
  await page.click('[data-act="add-cap"][data-c="0"]');
  await set('[data-bind="c.0.k.3.requirementRef"]', KONF);
  assert.equal(await page.locator('[data-bind="c.0.k.3.id"]').inputValue(), "cap-konf-14-1", "the id is minted from the requirement");
  await page.locator('[data-cap="c.0.k.3"] select[data-param]').selectOption("tls13");
  await page.locator('[data-cap="c.0.k.3"] input[data-stmt][value="s2"]').check();
  const s = await B.status();
  assert.match(s, /ADVICE-6.*cap-konf-14-1: binds parameter 'transport-crypto', which is declared 0 times/);
  assert.equal(await page.locator("#btn-download").isDisabled(), true, "a pack with an error cannot be downloaded");
}));

test("signing elsewhere: the prepared bytes, signed by openssl, prove the publisher; a later change asks for a new signature", {
  ...OPTS, skip: SKIP || (spawnSync("openssl", ["version"]).status !== 0 && "openssl is not installed"),
}, () => withBuilder(async B => {
  const { page, set } = B;
  await page.setInputFiles("#pick-open-folder", WORKED);
  await set('[data-bind="pack.version"]', "3a");
  await set('[data-bind="c.0.productVersion"]', "7.2");
  await set('[data-bind="c.0.version"]', "2026-11");
  await page.check('input[name="sign-mode"][value="elsewhere"]');
  const keyFile = path.join(B.tmp, "key.pem");
  fs.writeFileSync(keyFile, PEM);
  const pubPem = spawnSync("openssl", ["pkey", "-in", keyFile, "-pubout"], { encoding: "utf8" }).stdout;
  await page.locator("#f-pubkey").fill(pubPem);
  await page.locator("#f-pubkey").dispatchEvent("change");
  await B.settle();
  const pae = await B.download("#btn-prepare");
  assert.equal(path.basename(pae), "server-7-hardening-3a.pae");
  const sigFile = path.join(B.tmp, "x.sig");
  assert.equal(spawnSync("openssl", ["pkeyutl", "-sign", "-rawin", "-inkey", keyFile, "-in", pae, "-out", sigFile]).status, 0);
  await B.settle();
  await page.locator("#f-sig").fill(fs.readFileSync(sigFile).toString("base64"));
  await page.locator("#f-sig").dispatchEvent("change");
  assert.match(await B.status(), /Ready to publish.*proven/);
  const files = await unzip(await B.download("#btn-download"));
  const plan = await rules.jscAdviceImport(core.jscGraphFrom([]), await rules.jscAdvicePack(files), { trusted: { [VENDOR]: FIXTURE_PUB } });
  assert.equal(plan.label, "proven");
  await set('[data-bind="c.0.productVersion"]', "7.3");
  assert.match(await B.status(), /SIGN.*changed after the bytes to sign were prepared/);
}));

const CDEF = path.join(ROOT, "one-page-apps/tests/fixtures/component-definition-dbserver.json");
const NIST = "https://ns.nist.gov/sp800-53/req/";
const componentsOf = files => files.filter(f => f.path.startsWith("objects/component/")).map(f => JSON.parse(f.text));
const capsOf = c => Object.fromEntries((c.capabilities || []).map(k => [k["requirement-ref"] || k.id, k]));

test("an OSCAL component definition becomes Components and recommendations; what a pack cannot carry is named", OPTS, () => withBuilder(async B => {
  const { page, set } = B;
  await set('[data-bind="origin"]', "https://dbvendor.example");
  await set('[data-bind="publisher.ref"]', VENDOR);   // named here: the page supplies no publisher
  B.answers.push("https://backup-standard.example/req/");
  await page.setInputFiles("#pick-oscal", CDEF);
  await B.settle();
  assert.equal(B.prompts.length, 1, "one prefix asked for, for the one source that is neither NIST nor in a catalogue");
  assert.match(B.prompts[0], /backup-standard\.example\/catalog\.json/);
  const report = (await page.locator("#sec-import").innerText()).replace(/\s+/g, " ");
  assert.match(report, /2 component\(s\) with 5 recommendation\(s\)/);
  assert.match(report, /0 through the catalogue, 4 by the rule of the NIST SP 800-53 conversion, 1 by a prefix you gave/);
  assert.match(report, /1 product version\(s\) from a version prop/);
  assert.match(report, /Suggested values not placed: sc-08_odp \(set for the whole control implementation; load the catalogue to place it\)/);
  assert.match(report, /Kinds mapped: Example DB Backup Link: interconnection -> service/);
  assert.match(report, /components\[\]\.props ×1/);
  assert.match(report, /component-definition\.capabilities ×1/);
  assert.match(report, /back-matter\.resources \(other than sources\) ×1/);
  assert.match(report, /1 source\(s\) read through the back-matter\. 1 parameter reference\(s\) in the texts rewritten/);
  assert.match(report, /1 suggested value\(s\) keep an OSCAL Rev 4 parameter id \(ac-2\.1 ac-2\.1_prm_1\)/, "a Rev 4 id the catalogue would rename is named");
  assert.equal(await page.locator('[data-bind="pack.title"][data-lang="en"]').inputValue(), "Example DB Server 7 component definition");
  assert.equal(await page.locator('[data-bind="publisher.name"][data-lang="en"]').inputValue(), "Example DB Vendor Inc.");
  await set('[data-bind="pack.id"]', "https://dbvendor.example/pack/server-7-hardening");
  assert.match(await B.status(), /Ready to publish/);

  const files = await unzip(await B.download("#btn-download"));
  const [server, link] = componentsOf(files);
  assert.equal(server.id, "https://dbvendor.example/component/example-db-server-7");
  assert.equal(server["product-version"], "7");
  assert.equal(server.version, "2026-11");
  assert.equal(link.kind, "service");
  const caps = capsOf(server);
  assert.deepEqual(Object.keys(caps), [NIST + "SC-8", NIST + "AC-2", NIST + "AC-2.1", NIST + "AU-12"]);
  assert.deepEqual(caps[NIST + "SC-8"]["statement-ids"], ["smt"]);
  assert.equal(caps[NIST + "SC-8"].id, "cap-sc-8");
  assert.equal(caps[NIST + "SC-8"].description.en, "The server encrypts every client connection.\n\nsmt: Set net.tls.mode to requireTLS and disable every protocol below TLS 1.3; this protects the {param:sc-08_odp} of transmitted data.");
  assert.deepEqual(caps[NIST + "AC-2"]["statement-ids"], ["smt.e", "smt.g"]);
  assert.deepEqual(caps[NIST + "AC-2"]["parameter-bindings"], { "ac-02_odp.03": "the database administrator" });
  assert.deepEqual(caps[NIST + "AC-2.1"]["parameter-bindings"], { "ac-2.1_prm_1": "the user management API" }, "without the catalogue the Rev 4 id stays as it was");
  assert.equal(capsOf(link)["https://backup-standard.example/req/BAK-1"].id, "cap-bak-1");
}));

test("with the SP 800-53 catalogue loaded, the import places every value under the catalogue's names and passes ADVICE-5 and ADVICE-6", OPTS, () => withBuilder(async B => {
  const { page, set } = B;
  await page.setInputFiles("#pick-cat-folder", path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle"));
  await B.settle();
  assert.match(await page.locator("#cat-state").innerText(), /^1196 requirement\(s\)/);   // 1,014, then 1,016 (cp-10.3 and sc-19); since the second round of 2026-11-14 every withdrawn control is an object (182)
  await set('[data-bind="origin"]', "https://dbvendor.example");
  await set('[data-bind="publisher.ref"]', VENDOR);   // named here: the page supplies no publisher
  B.answers.push("");                    // the backup standard stays unresolved: its recommendation is set by hand
  await page.setInputFiles("#pick-oscal", CDEF);
  await B.settle();
  const report = (await page.locator("#sec-import").innerText()).replace(/\s+/g, " ");
  assert.match(report, /4 through the catalogue, 0 by the rule of the NIST SP 800-53 conversion, 0 by a prefix you gave, 1 not resolved/);
  assert.match(report, /Not resolved; set the requirement by hand: BAK-1/);
  assert.doesNotMatch(report, /Suggested values not placed/);
  assert.doesNotMatch(report, /Clauses the catalogue does not have/);
  assert.doesNotMatch(report, /Rev 4 parameter id/, "with the catalogue the Rev 4 id is renamed, so nothing is left to warn about");
  await set('[data-bind="pack.id"]', "https://dbvendor.example/pack/server-7-hardening");
  const s = await B.status();
  assert.doesNotMatch(s, /ADVICE-5|ADVICE-6/, "every clause and suggested value is one the catalogue declares");
  assert.match(s, /Ready to publish/);
  const [server] = componentsOf(await unzip(await B.download("#btn-download")));
  const caps = capsOf(server);
  assert.deepEqual(caps[NIST + "SC-8"]["parameter-bindings"], { "sc-08_odp": ["confidentiality", "integrity"] }, "set for the whole control implementation, placed where it is declared, as a list for a many-choice");
  assert.deepEqual(caps[NIST + "AC-2.1"]["parameter-bindings"], { "ac-02.01_odp": "the user management API" }, "the Rev 4 id renamed through alt-identifiers");
}));

/* NIST's own examples (oscal-content, public domain): the census inputs of
   drafts/cp-advice-1-census/. Their sources are back-matter references, one
   of them Rev 4, and their texts carry OSCAL's insert markup. */
test("NIST's example component definitions import with every control resolved and no OSCAL markup left", OPTS, () => withBuilder(async B => {
  const { page, set } = B;
  await set('[data-bind="origin"]', "https://vendor.example");
  const dir = path.join(ROOT, "drafts/cp-advice-1-census/inputs");
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith(".json")).sort()) {
    await page.click("#btn-new");
    await set('[data-bind="origin"]', "https://vendor.example");
    await page.setInputFiles("#pick-oscal", path.join(dir, f));
    await B.settle();
    const r = await page.evaluate(() => window.jscPackBuilder.report());
    assert.equal(B.prompts.length, 0, `${f}: no prefix asked for`);
    assert.deepEqual(r.unresolved, [], `${f}: every control resolved`);
    assert.equal(r.how.nist, r.caps, `${f}: by the SP 800-53 rule, through the back-matter`);
    const caps = (await page.evaluate(() => window.jscPackBuilder.draft())).components.flatMap(c => c.caps);
    assert.ok(caps.every(k => !/\{\{\s*insert:/.test(JSON.stringify(k.description))), `${f}: no OSCAL markup left`);
    if (/^example-component(-min)?\.json$/.test(f)) {
      assert.equal(r.notes.filter(n => /is a Rev 4 source/.test(n)).length, 2, `${f}: both Rev 4 sources named`);
      assert.ok(r.notes.some(n => /ac-2\.3 is implemented twice/.test(n)), `${f}: the double implementation named`);
    } else {
      assert.equal(r.clauses, 2, `${f}: both clause-level statements carried`);
      assert.equal(r.values, 2, `${f}: both values carried`);
      assert.ok(r.notes.some(n => /Rev 4 parameter id/.test(n)), `${f}: the Rev 4 parameter ids are named`);
    }
  }
}));
