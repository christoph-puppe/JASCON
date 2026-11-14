#!/usr/bin/env python3
"""attestation-binds on a bundle, end to end (backlog #46): the reference
validator is run on copies of the IFA bundle whose Attestation, beside the
manifest, was changed in one place each.

    python3 jascon/scripts/test_attestation_binds.py

The vectors (conformance/attestation-vectors.json, `binds-vectors`) hold
the primitive in every implementation. This file holds what a vector
cannot: that the validator finds the Attestation beside the manifest at
all, types and counts it, and fails the bundle when it does not bind."""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
IFA = os.path.join(ROOT, "converted_examples", "US.IFA-GoodRead", "ifa-core-bundle")
ATT = "attestation-ifa-ato.json"
AID = "https://ifa.gov/goodread/attestation/ifa-ato"

class AttestationBesideTheManifest(unittest.TestCase):
    def run_on(self, change=None, *args):
        """-> (exit code, the lines about this bundle). `change` edits the Attestation of a copy."""
        with tempfile.TemporaryDirectory() as tmp:
            bundle = os.path.join(tmp, "ifa-core-bundle")
            shutil.copytree(IFA, bundle)
            if change is not None:
                p = os.path.join(bundle, ATT)
                with open(p, encoding="utf-8") as f: att = json.load(f)
                change(att, bundle)
                if att is not None and os.path.exists(p):
                    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(json.dumps(att, indent=1, ensure_ascii=False) + "\n")
            r = subprocess.run([sys.executable, os.path.join(HERE, "validate_core.py"), bundle, "--as-of", "2026-11-14", *args],
                               capture_output=True, text=True)
            return r.returncode, r.stdout

    def test_backlog_46_the_attestation_beside_the_manifest_is_read_typed_and_bound(self):
        code, out = self.run_on()
        self.assertEqual(code, 0, out[-600:])
        self.assertIn(f"binds: {AID} = FULL MATCH [3 subject(s) of this bundle; this manifest]", out)
        self.assertIn("ifa-core-bundle: 18 pass, 0 fail", out)          # 16 objects, the manifest, the Attestation
        self.assertIn("'attestation': 1", out)

    def test_backlog_46_the_example_folder_is_held_to_its_two_attestations(self):
        # the example folder is validated with every run; its own Attestation binds its manifest, the vendor's the pack manifest it keeps
        code, out = self.run_on()
        self.assertEqual(code, 0, out[-600:])
        self.assertIn("binds: https://agency-x.example/attestation/acme-2026 = FULL MATCH [3 subject(s) of this bundle; this manifest]", out)
        self.assertIn("binds: https://dbvendor.example/attestation/server-7-hardening-3 = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]", out)
        self.assertIn("dsse: https://agency-x.example/attestation/acme-2026 = signature UNVERIFIED", out)
        # in verification mode, with the public key of the corpus fixture, both signatures verify
        code, out = self.run_on(None, "--trusted-keys", os.path.join(ROOT, "jascon", "conformance", "fixture-trusted-keys.json"))
        self.assertEqual(code, 0, out[-600:])
        self.assertIn("dsse: https://agency-x.example/attestation/acme-2026 = signature VERIFIED (Ed25519)", out)
        self.assertIn("dsse: https://dbvendor.example/attestation/server-7-hardening-3 = signature VERIFIED (Ed25519)", out)

    def test_backlog_46_a_subject_digest_that_is_not_the_objects_fails_the_bundle(self):
        def change(att, _):
            d = att["subject-semantic-digests"][0]["semantic-digest"]
            att["subject-semantic-digests"][0]["semantic-digest"] = d[:-1] + ("0" if d[-1] != "0" else "1")
        code, out = self.run_on(change)
        self.assertEqual(code, 1)
        self.assertIn(f"[attestation-binds] {AID}: subject https://ifa.gov/goodread/component/system1234: recomputed semantic digest", out)
        self.assertIn("ifa-core-bundle: 18 pass, 1 fail", out)

    def test_backlog_46_a_withdrawn_attestation_that_no_longer_binds_is_reported_and_fails_nothing(self):
        def change(att, _):
            d = att["subject-semantic-digests"][0]["semantic-digest"]
            att["subject-semantic-digests"][0]["semantic-digest"] = d[:-1] + ("0" if d[-1] != "0" else "1")
            att["lifecycle"] = "withdrawn"
        code, out = self.run_on(change)
        self.assertEqual(code, 0, out[-600:])
        self.assertIn(f"binds: {AID} = DOES NOT BIND [lifecycle withdrawn: reported, not a failure] subject https://ifa.gov/goodread/component/system1234: recomputed semantic digest", out)
        self.assertIn("ifa-core-bundle: 18 pass, 0 fail", out)

    def test_backlog_46_a_signed_attestation_is_not_withdrawn_by_editing_it(self):
        # The envelope signs the Attestation's canonical form, lifecycle included. Whoever edits the lifecycle of a
        # signed Attestation breaks its envelope, in every mode: withdrawing it is the signer's act. Without its
        # envelope it is an unsigned record, and a withdrawn one fails nothing.
        pack = os.path.join(ROOT, "jascon", "example-packs", "dbvendor-server-7-advice")
        name = "attestation-dbvendor-server-7-advice.json"
        def run(change):
            with tempfile.TemporaryDirectory() as tmp:
                bundle = os.path.join(tmp, "pack"); shutil.copytree(pack, bundle)
                p = os.path.join(bundle, name)
                with open(p, encoding="utf-8") as f: att = json.load(f)
                change(att)
                with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(json.dumps(att, indent=1, ensure_ascii=False) + "\n")
                r = subprocess.run([sys.executable, os.path.join(HERE, "validate_core.py"), bundle, "--as-of", "2026-11-14"], capture_output=True, text=True)
                return r.returncode, r.stdout
        code, out = run(lambda a: a.__setitem__("lifecycle", "withdrawn"))
        self.assertEqual(code, 1)
        self.assertIn("dsse: payload != the Attestation's canonical form (attestation-binds)", out)
        self.assertIn("pack: 3 pass, 1 fail", out)
        def unsigned_and_withdrawn(a): a["lifecycle"] = "withdrawn"; a.pop("envelope-ref")
        code, out = run(unsigned_and_withdrawn)
        self.assertEqual(code, 0, out[-600:])
        self.assertIn("= no envelope (unsigned attestation)", out)
        self.assertIn("pack: 3 pass, 0 fail", out)

    def test_backlog_46_a_subject_the_bundle_does_not_hold_fails_the_bundle(self):
        def change(att, _): att["subject-semantic-digests"][1]["id"] = "https://ifa.gov/goodread/impl/not-delivered"
        code, out = self.run_on(change)
        self.assertEqual(code, 1)
        self.assertIn("subject https://ifa.gov/goodread/impl/not-delivered: not an object of this bundle", out)

    def test_backlog_46_another_manifest_is_a_semantic_match_and_no_failure(self):
        def change(att, _): att["content-manifest-digest"] = "sha256:" + "0" * 64
        code, out = self.run_on(change)
        self.assertEqual(code, 0, out[-600:])
        self.assertIn(f"binds: {AID} = SEMANTIC MATCH [3 subject(s) of this bundle; another manifest", out)

    def test_backlog_46_a_changed_object_is_caught_by_the_attestation_too(self):
        # the manifest is re-pinned after the change, as somebody would who edits an object and wants a green run:
        # the two digests of the manifest then agree with the file, and only the Attestation still knows the old content
        def change(att, bundle):
            sys.path.insert(0, HERE)
            from oscal_conv_lib import semantic_digest
            import hashlib
            rel = "objects/impl/system1234-ac-6-1.json"
            p = os.path.join(bundle, rel)
            with open(p, encoding="utf-8") as f: o = json.load(f)
            o["status"] = "planned"
            raw = (json.dumps(o, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
            with open(p, "wb") as f: f.write(raw)
            mp = os.path.join(bundle, "content-manifest.json")
            with open(mp, encoding="utf-8") as f: m = json.load(f)
            e = next(x for x in m["objects"] if x["path"] == rel)
            e["package-digest"] = "sha256:" + hashlib.sha256(raw).hexdigest(); e["semantic-digest"] = semantic_digest(o)
            with open(mp, "w", encoding="utf-8", newline="\n") as f: f.write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
        code, out = self.run_on(change)
        self.assertEqual(code, 1)
        self.assertIn("subject https://ifa.gov/goodread/impl/system1234-ac-6.1: recomputed semantic digest", out)
        self.assertIn("another manifest", out)                           # the re-pinned manifest is not the one that was attested
        self.assertIn("ifa-core-bundle: 18 pass, 1 fail", out)          # and nothing else in the bundle objects

    def test_backlog_46_without_its_attestation_the_bundle_says_nothing_about_one(self):
        def change(att, bundle): os.remove(os.path.join(bundle, ATT))
        code, out = self.run_on(change)
        self.assertEqual(code, 0, out[-600:])
        self.assertNotIn(AID, out)                                       # no line about an Attestation that is not there
        self.assertIn("ifa-core-bundle: 17 pass, 0 fail", out)

if __name__ == "__main__":
    unittest.main()
