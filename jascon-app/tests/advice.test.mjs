/* Advice packs in the app (CP-ADVICE-1), beyond the conformance vectors of
   tests/rules.test.mjs: what the app does with a pack as files.

   What these tests prove, on the worked pack the repository ships
   (jascon/example-packs/dbvendor-server-7-advice) and on the example folder:
   - the pack manifests a set keeps under packs/sha256/ travel through load
     and export and are checked against their names;
   - a pack is read and held to its own manifest; the import plan adds the
     vendor's files as they are, keeps the vendor's manifest, and leaves
     every other object of the set as it was (the receipt is measured);
   - the same file again writes nothing;
   - another release replaces only what the earlier one brought, and names
     the edges that cite a capability it drops or changes;
   - what ADVICE-1, ADVICE-11 and a damaged pack refuse, with the rule's
     message, and that a refusal writes nothing;
   - adoption: the edge cites <product>#<capability>, holds under ADVICE-7
     once the product is a member, and a suggested value outside what a
     Tailoring allows is not written;
   - the set after import and adoption, exported, passes the Python
     reference validator (skipped where python3 with jsonschema is missing). */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, "../..");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js");
const rules = require("../jascon-rules.js");
const EXAMPLES = path.join(ROOT, "jascon/examples"), PACK = path.join(ROOT, "jascon/example-packs/dbvendor-server-7-advice");
const python = spawnSync("python3", ["-c", "import jsonschema"], { encoding: "utf8" }).status === 0;

const readTree = (dir, prefix = "") => fs.readdirSync(dir).sort().flatMap(n => fs.statSync(path.join(dir, n)).isDirectory()
  ? readTree(path.join(dir, n), prefix + n + "/") : [{ path: prefix + n, text: core.jscDecode(fs.readFileSync(path.join(dir, n))) }]);
const graphOf = files => core.jscGraphFrom(core.jscClassifyFiles(core.jscNormalizePaths(files).files).records);
/* the store, in memory: the records of a set, and a plan applied to them as jscSet.applyPack does */
const recordsOf = files => core.jscClassifyFiles(files).records.map(r => ({ ...r, origin: "imported" }));
const apply = (records, plan) => [...records.filter(r => !plan.deletes.includes(r.path) && !plan.writes.some(w => w.path === r.path)), ...plan.writes];
const save = (records, obj, type, p) => [...records.filter(r => r.id !== obj.id), { path: p, text: core.jscSerialize(obj), kind: "object", type, id: obj.id, origin: "authored" }];
const errorsOf = async g => (await rules.jscCheckGraph(g, await core.jscVerify(g))).findings.filter(f => f.kind === "error").map(f => f.message);

const P = "https://org.example", VENDOR = "https://dbvendor.example/component/server-7", REQ = "https://ns.bsi.bund.de/gspp/req/KONF.14.1";
/* a set of the user's: the requirement the advice is about with the facet schema it uses, and a system of one asset */
function baseSet() {
  const asset = { id: P + "/comp/db", version: "1", lifecycle: "draft", title: { en: "Order database" }, kind: "software",
    capabilities: [{ id: "cap-konf-14-1", "requirement-ref": REQ }] };
  const system = { id: P + "/comp/shop", version: "1", lifecycle: "draft", title: { en: "Shop" }, kind: "system", members: [{ "component-ref": asset.id }] };
  const edge = { id: P + "/impl/db-konf-14-1", version: "1", lifecycle: "draft", "component-ref": asset.id, "requirement-ref": REQ,
    responsibility: "provider", "satisfied-by": [{ "capability-ref": "cap-konf-14-1" }], status: "planned" };
  return [
    ...["req-konf-14-1.json", "gspp-taxonomy-1.0.0.json"].map(f => ({ path: f, text: core.jscDecode(fs.readFileSync(path.join(EXAMPLES, f))) })),
    { path: "objects/comp/db.json", text: core.jscSerialize(asset) }, { path: "objects/comp/shop.json", text: core.jscSerialize(system) },
    { path: "objects/impl/db-konf-14-1.json", text: core.jscSerialize(edge) },
  ];
}
/* another release of the worked pack, written the way a vendor would: the Component changed, the manifest recomputed */
async function release(version, change) {
  const files = readTree(PACK).filter(f => !f.path.startsWith("attestation-"));
  const manifest = JSON.parse(files.find(f => f.path === "content-manifest.json").text);
  const entry = manifest.objects[0], file = files.find(f => f.path === entry.path), comp = JSON.parse(file.text);
  change(comp);
  file.text = core.jscSerialize(comp);
  Object.assign(entry, { version: comp.version, "package-digest": await core.jscPackageDigest(file.text), "semantic-digest": await core.jscSemanticDigest(comp) });
  manifest.pack.version = version;
  files.find(f => f.path === "content-manifest.json").text = core.jscSerialize(manifest);
  return files;
}
function validate(files, label) {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-app-advice-"));
  for (const f of files) { fs.mkdirSync(path.dirname(path.join(out, f.path)), { recursive: true }); fs.writeFileSync(path.join(out, f.path), f.text); }
  const run = spawnSync("python3", [path.join(ROOT, "jascon/scripts/validate_core.py"), out], { encoding: "utf8" });
  const line = run.stdout.split("\n").find(l => l.includes(path.basename(out))) || "";
  fs.rmSync(out, { recursive: true });
  assert.match(line, / 0 fail/, label + "\n" + run.stdout.slice(-2000));
  return run.stdout;
}

test("a set keeps the pack manifests under packs/sha256/, whatever they are called, and every other file as before", () => {
  const kept = core.jscKeepFiles([
    { path: "b/content-manifest.json", text: "{}" },
    { path: "b/packs/sha256/" + "a".repeat(64), text: "{}" },
    { path: "b/packs/sha256/not-a-digest", text: "{}" },
    { path: "b/packs/sha256/deeper/file", text: "{}" },
    { path: "b/packs/readme", text: "x" },
  ]).map(e => e.path);
  assert.deepEqual(kept, ["b/content-manifest.json", "b/packs/sha256/" + "a".repeat(64), "b/packs/sha256/not-a-digest"]);
});

test("the example folder: its kept pack manifest is loaded, verified against its name, reported with its publisher, and exported byte for byte", async () => {
  const onDisk = readTree(EXAMPLES), g = graphOf(core.jscKeepFiles(onDisk));
  const kept = core.jscKeptPacks(g);
  assert.equal(kept.length, 1, "one kept pack manifest");
  assert.equal(await core.jscSha256(kept[0][1]), kept[0][0], "its name is the SHA-256 of its bytes");
  const v = await core.jscVerify(g);
  assert.deepEqual(v.packs, [{ path: "packs/sha256/" + kept[0][0], ok: true }]);
  const res = await rules.jscCheckGraph(g, v);
  assert.deepEqual(res.findings.filter(f => f.kind === "error"), []);
  assert.equal(res.packs.length, 1);
  assert.deepEqual([res.packs[0].id, res.packs[0].version, res.packs[0].status], ["https://dbvendor.example/pack/server-7-hardening", "3", "proven"]);
  assert.ok(res.findings.some(f => f.area === "advice" && f.kind === "note" && /kept pack \(1 object\(s\)\).*publisher PROVEN/.test(f.message)));
  const built = await core.jscBuildBundle(g);
  assert.equal(built.verbatim, true);
  const file = built.files.find(f => f.path === "packs/sha256/" + kept[0][0]);
  assert.equal(file && file.text, onDisk.find(f => f.path === "packs/sha256/" + kept[0][0]).text, "the kept manifest leaves as it came");
  /* a kept file that was changed no longer matches its name: ADVICE-8, and the digest check says so too */
  g.aux.find(a => a.path.startsWith("packs/sha256/")).text += " ";
  assert.equal((await core.jscVerify(g)).packs[0].ok, false);
  const errs = await errorsOf(g);
  assert.ok(errs.some(m => /does not match its name \(ADVICE-8/.test(m)), errs.join(" | "));
  /* the worked pack is the file the example folder imported: the same file again is a no-op */
  const g2 = graphOf(core.jscKeepFiles(onDisk)), plan = await rules.jscAdviceImport(g2, await rules.jscAdvicePack(readTree(PACK)));
  assert.equal(plan.result, "already-imported");
  assert.deepEqual([plan.writes, plan.deletes, plan.errors], [[], [], []]);
});

test("the worked pack as a bundle: read, held to its manifest, and its publisher proven by the attestation beside it", async () => {
  const pack = await rules.jscAdvicePack(readTree(PACK).map(f => ({ ...f, path: "unzipped/" + f.path })));
  assert.deepEqual(pack.problems, []);
  assert.deepEqual([...pack.objs.keys()], [VENDOR]);
  assert.equal(pack.digest, await core.jscSha256(fs.readFileSync(path.join(PACK, "content-manifest.json"), "utf8")));
  assert.equal(pack.attestations.length, 1);
  assert.ok(pack.attestations[0].envelope, "the envelope the attestation names came with it");
  /* checked as a set of its own, the pack passes: ADVICE-1..3 and the kernel pin */
  const res = await rules.jscCheckGraph(graphOf(readTree(PACK)), null);
  assert.deepEqual(res.findings.filter(f => f.kind === "error").map(f => f.message), []);
  assert.deepEqual(res.packs.map(p => [p.where, p.status]), [["pack", "proven"]]);
  assert.equal(await rules.jscAdvicePack([{ path: "a.json", text: "{}" }]), null, "a selection without a manifest is not a pack");
});

test("import: the vendor's files join the set as they are, the manifest is kept, nothing else changes; again is a no-op; adoption holds; python accepts the export", { skip: !python && "python3 with jsonschema not available" }, async () => {
  let records = recordsOf(baseSet());
  const pack = await rules.jscAdvicePack(readTree(PACK));
  const plan = await rules.jscAdviceImport(core.jscGraphFrom(records), pack);
  assert.equal(plan.result, "import");
  assert.deepEqual([plan.added, plan.replaced, plan.removed, plan.errors], [[VENDOR], [], [], []]);
  assert.equal(plan.publisher, "proven");
  assert.deepEqual(plan.pack, JSON.parse(pack.manifestText).pack);
  const before = records.map(r => r.text);
  records = apply(records, plan);
  assert.deepEqual(records.slice(0, before.length).map(r => r.text), before, "no file of the set was rewritten");
  const byPath = new Map(records.map(r => [r.path, r]));
  assert.equal(byPath.get("objects/component/server-7.json").text, fs.readFileSync(path.join(PACK, "objects/component/server-7.json"), "utf8"), "the vendor's Component byte for byte");
  assert.equal(byPath.get("packs/sha256/" + pack.digest).text, pack.manifestText, "the vendor's manifest, unchanged, under the name of its digest");
  assert.ok(byPath.has("attestation-dbvendor-server-7-advice.json") && byPath.has("attestation-dbvendor-server-7-advice.dsse"), "its attestation and envelope beside the manifest");
  assert.ok(plan.writes.every(w => w.origin === "pack"));
  let g = core.jscGraphFrom(records);
  const receipt = await rules.jscAdviceReceipt(plan, g);
  assert.equal(receipt.text, "unchanged 4 of 4 · added 1 components");
  assert.deepEqual(await errorsOf(g), []);
  assert.deepEqual((await rules.jscAdviceHeld(g, null)).packs.map(p => [p.id, p.version, p.status, p.objects]), [["https://dbvendor.example/pack/server-7-hardening", "3", "proven", [VENDOR]]]);
  /* the same file again */
  const again = await rules.jscAdviceImport(g, pack);
  assert.equal(again.result, "already-imported");
  assert.deepEqual([again.writes, again.deletes], [[], []]);
  /* adoption: an edge of the user's component that cites the vendor's capability */
  const objs = () => new Map([...g.objects].map(([id, r]) => [id, { type: r.type, obj: r.obj }]));
  const cap = id => g.objects.get(VENDOR).obj.capabilities.find(c => c.id === id);
  const edge = rules.jscAdviceEdge(objs(), P + "/comp/shop", VENDOR, cap("cap-tls"), { id: P + "/impl/shop-tls", copy: ["transport-crypto"] });
  assert.deepEqual(edge["satisfied-by"], [{ "capability-ref": VENDOR + "#cap-tls" }]);
  assert.deepEqual(edge["statement-refs"], ["s1"]);
  assert.deepEqual(edge["parameter-bindings"], { "transport-crypto": "tls13" }, "the ticked value fits and is copied");
  assert.equal(rules.jscAdviceEdge(objs(), P + "/comp/shop", VENDOR, cap("cap-audit-log"), { id: P + "/impl/x" }), null, "a capability about a requirement outside the set gives no edge");
  records = save(records, edge, "implementation", "objects/impl/shop-tls.json");
  g = core.jscGraphFrom(records);
  const notMember = await errorsOf(g);
  assert.equal(notMember.length, 1, notMember.join(" | "));
  assert.match(notMember[0], /is not a member of https:\/\/org\.example\/comp\/shop \(ADVICE-7/);
  const shop = g.objects.get(P + "/comp/shop").obj;
  records = save(records, { ...shop, members: [...shop.members, { "component-ref": VENDOR, context: "datastore" }] }, "component", "objects/comp/shop.json");
  g = core.jscGraphFrom(records);
  assert.deepEqual(await errorsOf(g), [], "with the product as a member the edge holds");
  /* a second capability on the same requirement and other clauses is an edge of its own; the same one again amends */
  const second = rules.jscAdviceEdge(objs(), P + "/comp/shop", VENDOR, cap("cap-key-rotation"), { id: P + "/impl/shop-rotation" });
  assert.equal(second.id, P + "/impl/shop-rotation");
  assert.equal(rules.jscAdviceEdge(objs(), P + "/comp/shop", VENDOR, cap("cap-tls"), { id: P + "/impl/other" }).id, P + "/impl/shop-tls");
  records = save(records, second, "implementation", "objects/impl/shop-rotation.json");
  g = core.jscGraphFrom(records);
  const built = await core.jscBuildBundle(g);
  assert.equal(built.manifest["kernel-version"], "2.0.0", "statement-ids on a capability and product-version need the kernel pin");
  assert.ok(!built.manifest.objects.some(e => e.path.startsWith("packs/")), "the kept manifest is not listed (ADVICE-8)");
  assert.ok(!("pack" in built.manifest), "the set is not a pack");
  assert.ok(built.files.some(f => f.path === "packs/sha256/" + pack.digest));
  const out = validate(built.files, "the set after import and adoption");
  assert.match(out, /kept pack \(1 object\(s\)\): https:\/\/dbvendor\.example\/pack\/server-7-hardening release 3/);
  /* loaded again from the export, the set is as it was: listed objects, the kept pack, no error */
  const back = graphOf(await core.jscUnzip(core.jscZip(built.files)));
  assert.deepEqual(await errorsOf(back), []);
  assert.equal(core.jscKeptPacks(back).length, 1);
  assert.equal((await rules.jscAdviceImport(back, pack)).result, "already-imported");
});

test("another release replaces what the earlier one brought and names the edges that cite a dropped or changed capability", async () => {
  let records = apply(recordsOf(baseSet()), await rules.jscAdviceImport(core.jscGraphFrom(recordsOf(baseSet())), await rules.jscAdvicePack(readTree(PACK))));
  const shop = JSON.parse(records.find(r => r.id === P + "/comp/shop").text);
  records = save(records, { ...shop, members: [...shop.members, { "component-ref": VENDOR }] }, "component", "objects/comp/shop.json");
  const cite = (n, cap) => ({ id: `${P}/impl/shop-${n}`, version: "1", lifecycle: "draft", "component-ref": P + "/comp/shop", "requirement-ref": REQ,
    "statement-refs": [n], responsibility: "provider", "satisfied-by": [{ "capability-ref": `${VENDOR}#${cap}` }], status: "planned" });
  records = save(save(records, cite("s1", "cap-tls"), "implementation", "objects/impl/shop-s1.json"), cite("s2", "cap-key-rotation"), "implementation", "objects/impl/shop-s2.json");
  let g = core.jscGraphFrom(records);
  assert.deepEqual(await errorsOf(g), []);
  const first = core.jscKeptPacks(g)[0][0];
  /* release 4: cap-tls is gone, cap-key-rotation says something else, cap-backup is new */
  const pack = await rules.jscAdvicePack(await release("4", comp => {
    comp.version = "2026-11";
    comp.capabilities = comp.capabilities.filter(c => c.id !== "cap-tls");
    comp.capabilities.find(c => c.id === "cap-key-rotation").description = { en: "Rotate every 60 days." };
    comp.capabilities.push({ id: "cap-backup", description: { en: "Back up with the dump command." } });
  }));
  assert.deepEqual(pack.problems, []);
  const plan = await rules.jscAdviceImport(g, pack);
  assert.equal(plan.result, "replace");
  assert.equal(plan.previous, "3");
  assert.deepEqual([plan.added, plan.replaced, plan.removed], [[], [VENDOR], []]);
  assert.deepEqual(plan.capabilities[VENDOR], { added: ["cap-backup"], removed: ["cap-tls"], changed: ["cap-key-rotation"] });
  assert.deepEqual(plan.dangling, [`${P}/impl/shop-s1 -> ${VENDOR}#cap-tls`]);
  assert.deepEqual(plan.affected, [{ edge: P + "/impl/shop-s1", ref: VENDOR + "#cap-tls", what: "removed" }, { edge: P + "/impl/shop-s2", ref: VENDOR + "#cap-key-rotation", what: "changed" }]);
  assert.equal(plan.publisher, "claimed", "release 4 came without an attestation");
  assert.ok(plan.deletes.includes("packs/sha256/" + first), "the earlier release's manifest leaves");
  assert.ok(plan.deletes.includes("attestation-dbvendor-server-7-advice.json") && plan.deletes.includes("attestation-dbvendor-server-7-advice.dsse"), "and its attestation with the envelope");
  records = apply(records, plan);
  g = core.jscGraphFrom(records);
  assert.deepEqual(core.jscKeptPacks(g).map(([name]) => name), [pack.digest], "one release of a pack in a set (ADVICE-10)");
  assert.equal((await rules.jscAdviceReceipt(plan, g)).text, "unchanged 6 of 6 · added 0 components");
  /* the edge that cited the dropped capability now points at nothing, as the preview said */
  const errs = await errorsOf(g);
  assert.equal(errs.length, 1, errs.join(" | "));
  assert.match(errs[0], /cites capability 'cap-tls', which https:\/\/dbvendor\.example\/component\/server-7 does not declare \(ADVICE-7/);
  /* the vendor's advice, edited in the set after the import, is no longer what the vendor published */
  const comp = JSON.parse(records.find(r => r.id === VENDOR).text);
  comp.capabilities[0].description = { en: "Edited by the user." };
  const edited = core.jscGraphFrom(save(records, comp, "component", records.find(r => r.id === VENDOR).path));
  assert.ok((await errorsOf(edited)).some(m => /the vendor's advice was edited after import \(ADVICE-9/.test(m)));
});

test("what is refused is refused with the rule's message, and a refusal writes nothing", async () => {
  const g = core.jscGraphFrom(recordsOf(baseSet()));
  const refused = async (files, rule, frag) => {
    const pack = await rules.jscAdvicePack(files), plan = await rules.jscAdviceImport(g, pack);
    assert.equal(plan.result, "refused", frag);
    assert.deepEqual([plan.writes, plan.deletes], [[], []], frag + ": nothing to write");
    assert.ok(plan.errors.some(([r, m]) => r === rule && m.includes(frag)), `${rule} with "${frag}"; got ${plan.errors.map(e => e.join(": ")).join(" | ")}`);
  };
  const withManifest = async (files, change) => {
    const out = files.map(f => ({ ...f })), mf = out.find(f => f.path === "content-manifest.json"), m = JSON.parse(mf.text);
    await change(m, out);
    mf.text = core.jscSerialize(m);
    return out;
  };
  const listed = async (obj, p) => ({ id: obj.id, version: obj.version, "package-digest": await core.jscPackageDigest(core.jscSerialize(obj)), "semantic-digest": await core.jscSemanticDigest(obj), path: p });
  /* ADVICE-1: a pack that lists a Tailoring */
  const tailoring = { id: "https://dbvendor.example/tailoring/t", version: "1", lifecycle: "active", selects: [{ "set-ref": "https://dbvendor.example/set/s" }] };
  await refused(await withManifest(readTree(PACK), async (m, files) => { m.objects.push(await listed(tailoring, "objects/t.json")); files.push({ path: "objects/t.json", text: core.jscSerialize(tailoring) }); }),
    "ADVICE-1", "is a tailoring - an advice pack holds components only");
  /* ADVICE-2: an object under the user's origin */
  const foreign = { id: P + "/comp/db", version: "9", lifecycle: "active", kind: "software" };
  await refused(await withManifest(readTree(PACK), async (m, files) => { m.objects.push(await listed(foreign, "objects/db.json")); files.push({ path: "objects/db.json", text: core.jscSerialize(foreign) }); }),
    "ADVICE-2", "is not under the pack's origin https://dbvendor.example");
  /* ADVICE-11: an id the set holds and no pack brought */
  const held = core.jscGraphFrom([...recordsOf(baseSet()), { path: "objects/comp/server-7.json", text: fs.readFileSync(path.join(PACK, "objects/component/server-7.json"), "utf8"), kind: "object", type: "component", id: VENDOR, origin: "imported" }]);
  const plan = await rules.jscAdviceImport(held, await rules.jscAdvicePack(readTree(PACK)));
  assert.equal(plan.result, "refused");
  assert.match(plan.errors[0][1], /is already in the set and not part of https:\/\/dbvendor\.example\/pack\/server-7-hardening \(ADVICE-11/);
  /* a bundle without a pack header is not a pack, and is not loaded over the set either */
  await refused(await withManifest(readTree(PACK), m => { delete m.pack; }), "ADVICE-11", "the manifest carries no pack header - this is not an advice pack");
  /* a pack must pin the kernel that knows its header */
  await refused(await withManifest(readTree(PACK), m => { delete m["kernel-version"]; }), "KERNEL-1", "the manifest carries a pack header, which needs kernel 2.0.0");
  /* a file that is not the one the manifest describes */
  await refused(readTree(PACK).map(f => (f.path.endsWith("server-7.json") ? { ...f, text: f.text.replace("requireTLS", "preferTLS") } : f)), "PACK", "objects/component/server-7.json: semantic-digest mismatch");
  await refused(readTree(PACK).filter(f => !f.path.endsWith("server-7.json")), "PACK", "objects/component/server-7.json: listed but missing");
  await refused([{ path: "content-manifest.json", text: "{ not json" }], "PACK", "content-manifest.json: not JSON");
});

test("adoption: a suggested value is offered only where it fits the declared space and every Tailoring that binds the parameter", () => {
  const req = { id: P + "/req/1", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [P + "/p"], prose: { en: "Use {param:proto}; at most {param:tries} tries; log to {param:sink}." },
    parameters: [{ name: "proto", type: "choice", cardinality: "one", choices: [{ value: "tls13", label: { en: "1.3" } }, { value: "tls12", label: { en: "1.2" } }] },
      { name: "tries", type: "integer", min: 1, max: 10, tightening: "lower" }, { name: "sink", type: "choice", cardinality: "one", choices: [{ value: "file", label: { en: "file" } }] }] }] };
  const set = { id: P + "/set/all", version: "1", lifecycle: "active", members: [{ ref: req.id }] };
  const tailoring = { id: P + "/tailoring/t", version: "1", lifecycle: "active", selects: [{ "set-ref": set.id }], operations: [
    { op: "set-parameter", "requirement-ref": req.id, "statement-id": "s1", parameter: "proto", value: "tls12" },
    { op: "set-parameter", "requirement-ref": req.id, "statement-id": "s1", parameter: "tries", value: 5 }] };
  const objs = new Map([[req.id, { type: "requirement", obj: req }], [set.id, { type: "requirementSet", obj: set }], [tailoring.id, { type: "tailoring", obj: tailoring }]]);
  const verdicts = bound => Object.fromEntries(rules.jscAdviceAdoption(objs, { id: "c", "requirement-ref": req.id, "parameter-bindings": bound }).bindings.map(b => [b.name, b.verdict]));
  assert.deepEqual(verdicts({ proto: "tls13", tries: 3, sink: "file" }), { proto: "outside-tailoring", tries: "fits", sink: "fits" }, "the Tailoring binds tls12; 3 tries is tighter than its 5");
  assert.deepEqual(verdicts({ proto: "tls12", tries: 8 }), { proto: "fits", tries: "outside-tailoring" }, "8 tries is looser than the Tailoring's 5");
  assert.deepEqual(verdicts({ proto: "ssl3", tries: "3", nothing: 1 }), { proto: "outside-declared", tries: "wrong-kind", nothing: "not-declared" });
  assert.deepEqual(verdicts.call(null, {}), {});
  const outside = rules.jscAdviceAdoption(new Map(), { id: "c", "requirement-ref": req.id, "parameter-bindings": { proto: "tls13" } });
  assert.deepEqual([outside.requirement, outside.bindings[0].verdict], [null, "no-requirement"]);
  /* without the Tailoring every value in the declared space fits */
  objs.delete(tailoring.id);
  assert.deepEqual(verdicts({ proto: "tls13", tries: 8 }), { proto: "fits", tries: "fits" });
  objs.set(tailoring.id, { type: "tailoring", obj: tailoring });
  /* only a fitting value that was ticked reaches the edge */
  const cap = { id: "c", "requirement-ref": req.id, "parameter-bindings": { proto: "tls13", tries: 3, sink: "file" } };
  const edge = rules.jscAdviceEdge(objs, P + "/comp/own", P + "/comp/product", cap, { id: P + "/impl/e", copy: ["proto", "tries"] });
  assert.deepEqual(edge["parameter-bindings"], { tries: 3 }, "proto is outside the Tailoring and not written; sink was not ticked");
  assert.deepEqual(edge["satisfied-by"], [{ "capability-ref": P + "/comp/product#c" }]);
  assert.equal(rules.jscMatchTypes(edge).join(), "implementation");
});

test("a capability id is derived from the requirement and unique within its component", () => {
  const taken = new Set();
  assert.deepEqual(["https://a.example/req/KONF.14.1", "https://b.example/other/KONF-14-1", "https://a.example/req/AC-2"].map(r => rules.jscCapabilityId(r, taken)), ["cap-konf-14-1", "cap-konf-14-1-2", "cap-ac-2"]);
});
