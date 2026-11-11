/* Tests for the DOM-free part of jascon-core.js. Run from the repository root:

     node --test "jascon-app/tests/*.test.mjs"

   What they prove, each against data the repository ships:
   - a bundle that is loaded and exported unchanged leaves byte for byte as it
     came, manifest included (every shipped bundle and the example bundle);
   - both digests of every object verify against the shipped manifests;
   - a bundle the app changed gets a new manifest that the Python reference
     validator accepts (this one needs python3 with jsonschema and is skipped
     where that is missing);
   - exporting twice gives the same bytes;
   - the canonical form agrees with the conformance vectors. */
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
const core = createRequire(import.meta.url)("../jascon-core.js");

/* every file under dir as {path, text}, path relative to dir with "/" */
function readTree(dir, prefix = "") {
  const out = [];
  for (const name of fs.readdirSync(dir).sort()) {
    const full = path.join(dir, name);
    if (fs.statSync(full).isDirectory()) out.push(...readTree(full, prefix + name + "/"));
    else out.push({ path: prefix + name, text: core.jscDecode(fs.readFileSync(full)) });
  }
  return out;
}
function loadGraph(files) {
  const norm = core.jscNormalizePaths(files);
  const { records, problems } = core.jscClassifyFiles(norm.files);
  return { graph: core.jscGraphFrom(records), problems };
}
function shippedBundles() {
  const base = path.join(ROOT, "converted_examples");
  return fs.readdirSync(base).sort().flatMap(corpus => {
    const dir = path.join(base, corpus);
    if (!fs.statSync(dir).isDirectory()) return [];
    return fs.readdirSync(dir).filter(d => d.endsWith("-bundle")).map(d => path.join(dir, d));
  });
}
const EXAMPLES = path.join(ROOT, "jascon", "examples");

for (const dir of [...shippedBundles(), EXAMPLES]) {
  const label = path.relative(ROOT, dir);
  test(`unchanged round trip: ${label}`, async () => {
    // the bundle sits in a folder, as it does when a folder is picked or unzipped
    const onDisk = readTree(dir);
    const { graph, problems } = loadGraph(onDisk.map(f => ({ ...f, path: "picked/" + f.path })));
    assert.deepEqual(problems, []);
    assert.deepEqual(graph.problems, []);
    const listed = graph.manifest.objects.length;
    assert.equal([...graph.objects.values()].filter(r => r.entry).length, listed, "every manifest entry has its object");

    const v = await core.jscVerify(graph);
    assert.equal(v.counts.bad, 0, "no digest mismatch");
    assert.equal(v.counts.ok, listed);
    assert.equal(v.counts.unlisted, 0);
    assert.equal(v.counts.missing, 0);
    assert.ok(v.pins.every(p => p.ok), "every pinned file verifies");

    const built = await core.jscBuildBundle(graph);
    assert.deepEqual(built.problems, []);
    assert.equal(built.verbatim, true, "nothing changed, so the manifest leaves as it came");
    const want = new Map(onDisk.map(f => [f.path, f.text]));
    for (const f of built.files) assert.equal(f.text, want.get(f.path), f.path + " is byte-identical");
    const jsonOnDisk = onDisk.filter(f => f.path.endsWith(".json")).map(f => f.path).sort();
    const jsonOut = built.files.filter(f => f.path.endsWith(".json")).map(f => f.path).sort();
    assert.deepEqual(jsonOut, jsonOnDisk, "no JSON file is lost or invented");

    const again = await core.jscBuildBundle(graph);
    assert.deepEqual(core.jscZip(again.files), core.jscZip(built.files), "a second export gives the same archive");
    const back = await core.jscUnzip(core.jscZip(built.files));
    assert.deepEqual(back, built.files.map(f => ({ path: f.path, text: f.text })), "ZIP round trip");
  });
}

const python = (() => {
  const r = spawnSync("python3", ["-c", "import jsonschema"], { encoding: "utf8" });
  return r.status === 0;
})();

test("a changed bundle gets a manifest the reference validator accepts", { skip: !python && "python3 with jsonschema not available" }, async () => {
  const dir = shippedBundles().find(d => d.includes("IFA"));
  const { graph } = loadGraph(readTree(dir));
  // the app's own write path: a new Risk, a pinned scale, and an edit to an imported object
  const taken = new Set([...graph.objects.values()].map(r => r.path));
  const scale = JSON.parse(fs.readFileSync(path.join(ROOT, "risk-catalogs/scales/likelihood-3.json"), "utf8"));
  const risk = { id: "https://org.example/risk/r-1", version: "1", lifecycle: "draft",
    scenario: { en: "A test scenario." }, "owner-ref": "https://org.example/party/ciso", state: "identified" };
  const edited = [...graph.objects.values()].find(r => r.type === "component");
  const editedObj = { ...edited.obj, annotations: { ...(edited.obj.annotations || {}), note: "edited in the app" } };
  const records = [
    { path: core.JSC_MANIFEST, text: graph.manifestText, kind: "manifest" },
    ...[...graph.objects.values()].filter(r => r !== edited).map(r => ({ path: r.path, text: r.text, kind: "object", type: r.type, origin: "imported" })),
    { path: edited.path, text: core.jscSerialize(editedObj), kind: "object", type: "component", origin: "authored" },
    { path: core.jscObjectPath("risk", risk.id, taken), text: core.jscSerialize(risk), kind: "object", type: "risk", origin: "authored" },
    { path: "scales/likelihood-3.json", text: core.jscSerialize(scale), kind: "scale" },
    ...graph.facetSchemas.map(x => ({ path: x.path, text: x.text, kind: "facet-schema" })),
  ];
  const g2 = core.jscGraphFrom(records);
  const built = await core.jscBuildBundle(g2);
  assert.equal(built.verbatim, false);
  assert.equal(built.manifest["kernel-version"], "2.0.0");
  assert.equal(built.manifest.objects.length, graph.manifest.objects.length + 1);
  assert.equal(built.manifest.scales.length, 1);
  assert.equal(built.manifest.provenance["edited-with"], core.JSC_TOOL);

  // the validator reads bundle paths relative to the repository; a temp
  // folder outside it works because only the report label uses that
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-app-test-"));
  for (const f of built.files) {
    fs.mkdirSync(path.dirname(path.join(out, f.path)), { recursive: true });
    fs.writeFileSync(path.join(out, f.path), f.text);
  }
  const run = spawnSync("python3", [path.join(ROOT, "jascon/scripts/validate_core.py"), out], { encoding: "utf8" });
  const bundleLine = run.stdout.split("\n").find(l => l.includes(path.basename(out))) || "";
  assert.match(bundleLine, / 0 fail/, run.stdout.slice(-1500));
  assert.equal(run.status, 0, run.stdout.slice(-1500));
  fs.rmSync(out, { recursive: true });
});

test("an attestation the manifest does not list stays beside it", async () => {
  const { graph } = loadGraph(readTree(EXAMPLES));
  const att = [...graph.objects.values()].filter(r => r.type === "attestation");
  assert.ok(att.length > 0 && att.every(r => !r.entry), "the example bundle keeps its attestation unlisted");
  const built = await core.jscBuildBundle(graph);
  assert.ok(!built.manifest.objects.some(e => e.path === att[0].path));
  assert.ok(built.files.some(f => f.path === att[0].path), "but the file is shipped");
});

test("a kernel pin this app does not implement stops the load and names both versions", () => {
  const files = [{ path: core.JSC_MANIFEST, text: JSON.stringify({ "manifest-version": "1", "kernel-version": "3.0.0", objects: [] }) }];
  assert.throws(() => core.jscClassifyFiles(files), e => e instanceof core.JscKernelError && /3\.0\.0/.test(e.message) && /2\.0\.0/.test(e.message));
});

test("one unreadable file is a problem entry, not the end of the load", () => {
  const files = [
    { path: "objects/a.json", text: "{ not json" },
    { path: "objects/b.json", text: JSON.stringify({ id: "https://x.example/set/b", version: "1", lifecycle: "active", members: [] }) },
  ];
  const { records, problems } = core.jscClassifyFiles(files);
  assert.equal(problems.length, 1);
  assert.equal(core.jscGraphFrom(records).objects.size, 1);
});

test("canonical form agrees with the conformance vectors", () => {
  const v = JSON.parse(fs.readFileSync(path.join(ROOT, "jascon/conformance/jcs-vectors.json"), "utf8"));
  const cases = v.vectors.filter(c => c.canonical != null);
  assert.ok(cases.length >= 6);
  for (const c of cases) assert.equal(core.jscCanonical(c.input), c.canonical, c.name);
});

test("the pure-JS SHA-256 agrees with the platform's", async () => {
  for (const text of ["", "abc", "ä€𝄞", "x".repeat(55), "x".repeat(56), "x".repeat(64), "x".repeat(1000)]) {
    assert.equal(core.jscSha256Js(core.jscUtf8(text)), await core.jscSha256(text));
  }
});

test("text primitive: wanted language, then English, then what is there", () => {
  assert.equal(core.jscText({ en: "a", de: "b" }, "de"), "b");
  assert.equal(core.jscText({ en: "a" }, "de"), "a");
  assert.equal(core.jscText({ fr: ["x", "y"] }, "de"), "x y");
  assert.equal(core.jscText({ de: "b" }, "de-AT"), "b");
  assert.equal(core.jscText("plain", "de"), "plain");
  assert.equal(core.jscText(undefined, "de"), "");
});

test("a set keeps text files and the envelope an attestation names, whatever the envelope is called", () => {
  const kept = core.jscKeepFiles([
    { path: "b/attestation.json", text: '{"id":"https://x/att","envelope-ref": "env-1"}' },
    { path: "b/env-1", text: '{"payloadType":"x"}' },
    { path: "b/other-file", text: "not named by anything" },
    { path: "b/picture.png", text: "binary" },
    { path: "b/sig.dsse", text: "{}" },
  ]).map(e => e.path);
  assert.deepEqual(kept, ["b/attestation.json", "b/sig.dsse", "b/env-1"]);
});
