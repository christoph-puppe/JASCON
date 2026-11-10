/* The two checks that keep the app's words in step with its code:
   every interface string has a German text, and the settings table in
   readme.md is the one generated from JSC_CFG. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { findMissing } from "../tools/check-i18n.mjs";
import { render } from "../tools/gen-docs.mjs";

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
