#!/usr/bin/env python3
"""attestation-binds on a bundle, end to end (backlog #46), and MANIFEST-1
(backlog #75): a validator is run on copies of two shipped bundles whose
Attestation, beside the manifest, was changed in one place each, or was
entered in the manifest.

    python3 jascon/scripts/test_attestation_binds.py          the Python reference
    JASCON_TWIN="powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File jascon\\scripts\\validate_core.ps1" \\
        python jascon/scripts/test_attestation_binds.py        the PowerShell twin

The vectors (conformance/attestation-vectors.json, `binds-vectors`) hold
the primitive in every implementation. This file holds what a vector
cannot: that the validator finds the Attestation beside the manifest at
all, types and counts it, fails the bundle when a claimed Attestation does
not bind, and says so in the words both validators share. Every repository
bundle is a Full Match, so without the changed copies the lines for a
Semantic Match, for an Attestation that does not bind and for a failure
would never be printed - on Windows PowerShell 5.1 least of all.

All copies are validated in ONE run of the validator (the twin needs half
a minute for the vectors alone); each test reads the lines of its copy.
"""
import hashlib, json, os, re, shlex, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
IFA = os.path.join(ROOT, "converted_examples", "US.IFA-GoodRead", "ifa-core-bundle")
PACK = os.path.join(ROOT, "jascon", "example-packs", "dbvendor-server-7-advice")
KEYS = os.path.join(ROOT, "jascon", "conformance", "fixture-trusted-keys.json")
IFA_ATT, PACK_ATT = "attestation-ifa-ato.json", "attestation-dbvendor-server-7-advice.json"
AID = "https://ifa.gov/goodread/attestation/ifa-ato"
VID = "https://dbvendor.example/attestation/server-7-hardening-3"
TWIN = os.environ.get("JASCON_TWIN")        # the command that runs validate_core.ps1; unset: the reference
AS_OF = "2026-11-14"

def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
def read_json(path):
    with open(path, encoding="utf-8") as f: return json.load(f)

# ---- the copies: name -> (the bundle it is a copy of, the Attestation's file, what is changed) ----
def other_digest(att, _):
    d = att["subject-semantic-digests"][0]["semantic-digest"]
    att["subject-semantic-digests"][0]["semantic-digest"] = d[:-1] + ("0" if d[-1] != "0" else "1")
def other_digest_withdrawn(att, bundle): other_digest(att, bundle); att["lifecycle"] = "withdrawn"
def not_delivered(att, _): att["subject-semantic-digests"][1]["id"] = "https://ifa.gov/goodread/impl/not-delivered"
def other_manifest(att, _): att["content-manifest-digest"] = "sha256:" + "0" * 64
def object_changed_and_repinned(att, bundle):
    # the manifest is re-pinned after the change, as somebody would who edits an object and wants a green run: the
    # two digests of the manifest then agree with the file, and only the Attestation still knows the old content
    sys.path.insert(0, HERE)
    from oscal_conv_lib import semantic_digest
    rel = "objects/impl/system1234-ac-6-1.json"
    p = os.path.join(bundle, *rel.split("/"))
    o = read_json(p); o["status"] = "planned"
    raw = (json.dumps(o, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    with open(p, "wb") as f: f.write(raw)
    mp = os.path.join(bundle, "content-manifest.json")
    m = read_json(mp)
    e = next(x for x in m["objects"] if x["path"] == rel)
    e["package-digest"] = "sha256:" + hashlib.sha256(raw).hexdigest(); e["semantic-digest"] = semantic_digest(o)
    write_json(mp, m)
def removed(att, bundle): os.remove(os.path.join(bundle, IFA_ATT)); return "removed"
def withdrawn(att, _): att["lifecycle"] = "withdrawn"
def withdrawn_and_unsigned(att, _): att["lifecycle"] = "withdrawn"; att.pop("envelope-ref")
def listed_in_the_manifest(att_file):
    # backlog #75: the Attestation is moved under objects/ and entered in the manifest with both digests, as the IFA
    # bundle had it until 2026-11-13. Nothing else is wrong with such a bundle: every digest of the manifest is right.
    def change(att, bundle):
        sys.path.insert(0, HERE)
        from oscal_conv_lib import semantic_digest
        rel = "objects/attestation/" + att_file
        os.makedirs(os.path.join(bundle, "objects", "attestation"), exist_ok=True)
        os.rename(os.path.join(bundle, att_file), os.path.join(bundle, *rel.split("/")))
        with open(os.path.join(bundle, *rel.split("/")), "rb") as f: raw = f.read()
        mp = os.path.join(bundle, "content-manifest.json")
        m = read_json(mp)
        m["objects"].append({"id": att["id"], "version": att["version"], "path": rel,
                             "package-digest": "sha256:" + hashlib.sha256(raw).hexdigest(), "semantic-digest": semantic_digest(att)})
        write_json(mp, m)
        return "removed"                # no longer beside the manifest: nothing to write back there
    return change

COPIES = {
    "c01-as-shipped": (IFA, IFA_ATT, None),
    "c02-other-digest": (IFA, IFA_ATT, other_digest),
    "c03-other-digest-withdrawn": (IFA, IFA_ATT, other_digest_withdrawn),
    "c04-not-delivered": (IFA, IFA_ATT, not_delivered),
    "c05-other-manifest": (IFA, IFA_ATT, other_manifest),
    "c06-object-changed": (IFA, IFA_ATT, object_changed_and_repinned),
    "c07-no-attestation": (IFA, IFA_ATT, removed),
    "c08-signed-withdrawn": (PACK, PACK_ATT, withdrawn),
    "c09-unsigned-withdrawn": (PACK, PACK_ATT, withdrawn_and_unsigned),
    "c10-listed": (IFA, IFA_ATT, listed_in_the_manifest(IFA_ATT)),
    "c11-pack-listed": (PACK, PACK_ATT, listed_in_the_manifest(PACK_ATT)),
}

def validator(dirs, *more):
    if TWIN:
        cmd = shlex.split(TWIN, posix=(os.name != "nt")) + list(dirs) + ["-AsOf", AS_OF]
        if "--trusted-keys" in more: cmd += ["-TrustedKeys", KEYS]
    else:
        cmd = [sys.executable, os.path.join(HERE, "validate_core.py")] + list(dirs) + ["--as-of", AS_OF] + list(more)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    return r.returncode, r.stdout.replace("\r\n", "\n")

class AttestationBesideTheManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="binds-")
        dirs = []
        for name, (src, att_file, change) in COPIES.items():
            bundle = os.path.join(cls.tmp, name)
            shutil.copytree(src, bundle); dirs.append(bundle)
            if change is None: continue
            p = os.path.join(bundle, att_file)
            att = read_json(p)
            if change(att, bundle) != "removed": write_json(p, att)
        # One folder is named with a trailing separator. However a caller spells a folder, the bundle in it is the
        # same: the twin once cut relative paths off at the length of the spelling it was given, and reported every
        # object of such a folder as "on disk but not in manifest" (found on the workflow's Windows runner, whose
        # temporary folder has a short name that Windows spells out when it lists files).
        dirs[0] += os.sep
        cls.code, cls.out = validator(dirs)
        # the lines of each copy: from the end of the copy before it to its own summary line
        cls.block, cls.counts, at = {}, {}, 0
        for name in COPIES:
            m = re.search(r"^.*" + re.escape(name) + r": (\d+) pass, (\d+) fail.*$", cls.out[at:], re.M)
            assert m, f"no summary line for {name} in:\n{cls.out[-3000:]}"
            cls.block[name] = cls.out[at:at + m.end()]
            cls.counts[name] = (int(m.group(1)), int(m.group(2)))
            at += m.end()
        cls.rest = cls.out[at:]           # what follows the copies: the reference's example folder, the list of failures

    @classmethod
    def tearDownClass(cls): shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_backlog_46_the_attestation_beside_the_manifest_is_read_typed_and_bound(self):
        b = self.block["c01-as-shipped"]
        self.assertIn(f"binds: {AID} = FULL MATCH [3 subject(s) of this bundle; this manifest]", b)
        self.assertEqual(self.counts["c01-as-shipped"], (18, 0))          # 16 objects, the manifest, the Attestation
        self.assertRegex(b, r"'attestation': 1|attestation=1")
        self.assertIn(f"dsse: {AID} = no envelope (unsigned attestation)", b)

    def test_backlog_46_a_subject_digest_that_is_not_the_objects_fails_the_bundle(self):
        self.assertEqual(self.counts["c02-other-digest"], (18, 1))
        self.assertIn(f"[attestation-binds] {AID}: subject https://ifa.gov/goodread/component/system1234: recomputed semantic digest sha256:", self.rest)
        self.assertNotIn("binds:", self.block["c02-other-digest"])        # a failure is a failure, not a line of the report
        self.assertEqual(self.code, 1)

    def test_backlog_46_a_withdrawn_attestation_that_no_longer_binds_is_reported_and_fails_nothing(self):
        self.assertEqual(self.counts["c03-other-digest-withdrawn"], (18, 0))
        self.assertIn(f"binds: {AID} = DOES NOT BIND [lifecycle withdrawn: reported, not a failure] "
                      f"subject https://ifa.gov/goodread/component/system1234: recomputed semantic digest", self.block["c03-other-digest-withdrawn"])

    def test_backlog_46_a_subject_the_bundle_does_not_hold_fails_the_bundle(self):
        self.assertEqual(self.counts["c04-not-delivered"], (18, 1))
        self.assertIn("subject https://ifa.gov/goodread/impl/not-delivered: not an object of this bundle", self.rest)

    def test_backlog_46_another_manifest_is_a_semantic_match_and_no_failure(self):
        self.assertEqual(self.counts["c05-other-manifest"], (18, 0))
        self.assertIn(f"binds: {AID} = SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]",
                      self.block["c05-other-manifest"])

    def test_backlog_46_a_changed_object_is_caught_by_the_attestation_too(self):
        self.assertEqual(self.counts["c06-object-changed"], (18, 1))     # nothing else in the bundle objects
        m = re.search(r"\[attestation-binds\] [^\n]*subject https://ifa\.gov/goodread/impl/system1234-ac-6\.1: recomputed semantic digest [^\n]*", self.rest)
        self.assertTrue(m, self.rest[-1500:])
        self.assertIn("another manifest", m.group(0))                    # the re-pinned manifest is not the one that was attested

    def test_backlog_46_without_its_attestation_the_bundle_says_nothing_about_one(self):
        self.assertEqual(self.counts["c07-no-attestation"], (17, 0))
        self.assertNotIn(AID, self.block["c07-no-attestation"])

    def test_backlog_46_a_signed_attestation_is_not_withdrawn_by_editing_it(self):
        # The envelope signs the Attestation's canonical form, lifecycle included. Whoever edits the lifecycle of a
        # signed Attestation breaks its envelope, in every mode: withdrawing it is the signer's act. Without its
        # envelope it is an unsigned record, and a withdrawn one fails nothing.
        self.assertEqual(self.counts["c08-signed-withdrawn"], (3, 1))
        self.assertIn(f"{VID}: dsse: payload != the Attestation's canonical form (attestation-binds)", self.rest)
        self.assertEqual(self.counts["c09-unsigned-withdrawn"], (3, 0))
        self.assertIn(f"dsse: {VID} = no envelope (unsigned attestation)", self.block["c09-unsigned-withdrawn"])

    def test_backlog_75_an_attestation_the_manifest_lists_fails_the_bundle(self):
        # MANIFEST-1. Until 2026-11-14 this copy passed in both validators (18 pass, 0 fail): its only trace was the
        # verdict, a Semantic Match, because a manifest that lists an Attestation cannot be the one it binds.
        self.assertEqual(self.counts["c10-listed"], (18, 1))
        self.assertIn(f"{AID}: an Attestation is listed in the content manifest (MANIFEST-1: Attestations are excluded "
                      f"from the content manifest by definition, D3.1", self.rest)
        # it is still read with the bundle and held to what it binds
        self.assertIn(f"binds: {AID} = SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]",
                      self.block["c10-listed"])
        self.assertRegex(self.block["c10-listed"], r"'attestation': 1|attestation=1")

    def test_backlog_75_in_a_pack_both_rules_speak(self):
        # a pack holds Components only (ADVICE-1), and no manifest lists an Attestation (MANIFEST-1)
        self.assertEqual(self.counts["c11-pack-listed"], (3, 2))
        self.assertIn(f"{VID} is a attestation - an advice pack holds components only (an attestation travels beside the manifest, D3.1)", self.rest)
        self.assertIn(f"{VID}: an Attestation is listed in the content manifest (MANIFEST-1", self.rest)

    @unittest.skipIf(TWIN, "with a bundle named, the twin does not read the example folder; its default run does")
    def test_backlog_75_the_example_folder_is_held_to_it_too(self):
        # The reference reads jascon/examples beside its own file. A copy of the reference in a small tree of its own
        # reads a changed copy of the folder: the folder's own Attestation entered in its manifest, both digests right.
        sys.path.insert(0, HERE)
        from oscal_conv_lib import semantic_digest
        mirror = os.path.join(self.tmp, "mirror")
        for part in ("schemas", "conformance", "examples"):
            shutil.copytree(os.path.join(ROOT, "jascon", part), os.path.join(mirror, "jascon", part))
        os.makedirs(os.path.join(mirror, "jascon", "scripts"))
        shutil.copy2(os.path.join(HERE, "validate_core.py"), os.path.join(mirror, "jascon", "scripts", "validate_core.py"))
        ex, name, aid = os.path.join(mirror, "jascon", "examples"), "attestation-acme-2026.json", "https://agency-x.example/attestation/acme-2026"
        with open(os.path.join(ex, name), "rb") as f: raw = f.read()
        att = json.loads(raw.decode("utf-8"))
        self.assertEqual(att["id"], aid)
        m = read_json(os.path.join(ex, "content-manifest.json"))
        m["objects"].append({"id": aid, "version": att["version"], "path": name,
                             "package-digest": "sha256:" + hashlib.sha256(raw).hexdigest(), "semantic-digest": semantic_digest(att)})
        write_json(os.path.join(ex, "content-manifest.json"), m)
        r = subprocess.run([sys.executable, os.path.join(mirror, "jascon", "scripts", "validate_core.py"),
                            os.path.join(self.tmp, "c07-no-attestation"), "--as-of", AS_OF],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=mirror)
        out = r.stdout.replace("\r\n", "\n")
        self.assertEqual(r.returncode, 1, out[-800:])
        self.assertIn("skill-examples: 27 pass, 1 fail", out)
        self.assertIn(f"[skill-examples] {aid}: an Attestation is listed in the content manifest (MANIFEST-1", out)
        self.assertRegex(out, r"(?m)^1 FAILURES:$")          # this one and no other: the copied bundle beside it is clean

    def test_backlog_46_the_failures_are_these_and_no_others(self):
        failed = {name for name, (_, bad) in self.counts.items() if bad}
        self.assertEqual(failed, {"c02-other-digest", "c04-not-delivered", "c06-object-changed", "c08-signed-withdrawn",
                                  "c10-listed", "c11-pack-listed"})

    @unittest.skipIf(TWIN, "with a bundle named, the twin does not read the example folder; its default run does")
    def test_backlog_46_the_example_folder_is_held_to_its_two_attestations(self):
        # the reference validates the example folder with every run; its own Attestation binds its manifest, the vendor's
        # the pack manifest it keeps
        self.assertIn("binds: https://agency-x.example/attestation/acme-2026 = FULL MATCH [3 subject(s) of this bundle; this manifest]", self.rest)
        self.assertIn(f"binds: {VID} = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]", self.rest)
        self.assertIn("dsse: https://agency-x.example/attestation/acme-2026 = signature UNVERIFIED", self.rest)
        self.assertIn("skill-examples: 27 pass, 0 fail", self.rest)
        # in verification mode, with the public key of the corpus fixture, both signatures verify
        code, out = validator([os.path.join(self.tmp, "c01-as-shipped")], "--trusted-keys", KEYS)
        self.assertEqual(code, 0, out[-600:])
        self.assertIn("dsse: https://agency-x.example/attestation/acme-2026 = signature VERIFIED (Ed25519)", out)
        self.assertIn(f"dsse: {VID} = signature VERIFIED (Ed25519)", out)

    @unittest.skipUnless(TWIN, "the reference covers verification mode in the example-folder test")
    def test_backlog_46_the_twin_verifies_the_worked_pack_with_the_fixture_key(self):
        code, out = validator([PACK], "--trusted-keys")
        self.assertEqual(code, 0, out[-600:])
        self.assertIn(f"dsse: {VID} = signature VERIFIED (Ed25519)", out)
        self.assertIn(f"binds: {VID} = FULL MATCH [1 subject(s) of this bundle; this manifest]", out)

if __name__ == "__main__":
    unittest.main()
