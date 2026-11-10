/* The checks that keep what is generated or translated in step with its
   source: every interface string has a German text, the settings table in
   readme.md is the one generated from JSC_CFG, and jascon-schema.js is the
   one generated from the kernel schema. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { findMissing } from "../tools/check-i18n.mjs";
import { render } from "../tools/gen-docs.mjs";
import { render as renderSchema } from "../tools/gen-schema.mjs";
import { render as renderPresets } from "../tools/gen-presets.mjs";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("every interface string has a German translation", () => {
  const r = findMissing();
  assert.ok(r.used > 50, "the scanner found the strings at all");
  assert.deepEqual(r.missing, []);
});

test("the settings table in readme.md is the generated one", () => {
  const readme = fs.readFileSync(path.join(APP, "readme.md"), "utf8");
  assert.equal(render(readme), readme, "run node jascon-app/tools/gen-docs.mjs");
});

test("jascon-schema.js is the one generated from jascon/schemas/", () => {
  assert.equal(fs.readFileSync(path.join(APP, "jascon-schema.js"), "utf8"), renderSchema(), "run node jascon-app/tools/gen-schema.mjs");
});

test("jascon-presets.js is the one generated from the shipped scales and catalogues", () => {
  assert.equal(fs.readFileSync(path.join(APP, "jascon-presets.js"), "utf8"), renderPresets(), "run node jascon-app/tools/gen-presets.mjs");
});
