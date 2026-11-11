/* A catalog in the shape of a CIS Benchmark's OSCAL export, written for the
   tests: the repository may not carry a CIS Benchmark (CIS terms). The norm
   sits in the title and the statement is empty; there are audit and
   remediation parts, automated/manual and xccdf markings, CIS Controls
   safeguards of v7 and v8 in the back-matter, and profiles as linked
   resources. Every text in it is invented. Used by oscal.test.mjs (the CIS
   preset against its Python converter) and checks.test.mjs (the Checks tool). */
export function cisSynthetic() {
  const lab = v => ({ name: "label", value: v }), mark = (v, cls) => ({ name: "marking", value: v, ...(cls ? { class: cls } : {}) });
  const rule = (id, title, method, links, controls, extra = {}) => ({
    id, title, props: [lab(id), mark(`xccdf_id: xccdf_org.example_rule_${id}_synthetic`), mark(method)], links: links.map(h => ({ href: h, rel: "reference" })),
    parts: [
      { id: `${id}_smt`, name: "statement", props: [lab("Description")], prose: `Synthetic description of rule ${id}.` },
      { id: `${id}_rat`, name: "statement", props: [lab("Rationale")], prose: `Synthetic rationale of rule ${id}.` },
      { id: `${id}_aud`, name: "assessment-method", props: [lab("Audit")], prose: extra.audit || `Run a synthetic command and verify the output for rule ${id}.` },
      { id: `${id}_rem`, name: "guidance", props: [lab("Remediation")], prose: `Synthetic remediation of rule ${id}.` },
      { id: `${id}_cc`, name: "guidance", class: "CIS_Controls", props: [lab("CIS Controls")], links: controls.map(h => ({ href: h, rel: "reference" })) },
      { id: `${id}_ref`, name: "guidance", class: "References", props: [lab("References"), mark(`Synthetic reference for ${id}`, "Reference")] },
    ] });
  const res = (uuid, title, props, href) => ({ uuid, title, props, ...(href ? { rlinks: [{ href }] } : {}) });
  return { catalog: { uuid: "00000000-0000-4000-8000-000000000001",
    metadata: { title: "CIS Ubuntu Linux 24.04 LTS Benchmark", version: "0.0.0-synthetic", "oscal-version": "1.1.2", "last-modified": "2026-11-11T00:00:00Z" },
    groups: [
      { id: "1", title: "Initial Setup", props: [lab("1")], parts: [{ id: "1_ov", name: "overview", prose: "Synthetic overview of section 1." }],
        groups: [{ id: "1.1", title: "Filesystem", props: [lab("1.1")], controls: [
          rule("1.1.1", "Ensure a synthetic mount option is set", "automated", ["#p-l1s", "#p-l2w", "#d-1"], ["#s-8-4.1", "#s-7-9.2"]),
          rule("1.1.2", "Ensure a synthetic setting is reviewed", "manual", ["#p-l2w", "#missing"], ["#s-bad", "#s-8-12"]) ] }] },
      { id: "5", title: "Access Control", groups: [
        { id: "5.1", title: "SSH Server", controls: [
          rule("5.1.1", "Ensure sshd limits authentication attempts", "automated", ["#p-l1s"], ["#s-8-4.1"],
            { audit: "Run sshd -T and verify that maxauthtries is 4 or less." }) ] },
        { id: "5.2", title: "Privilege Escalation", controls: [rule("5.2.1", "Ensure a synthetic sudo option is set", "automated", [], [])] } ],
        controls: [rule("5.9", "Ensure a synthetic rule directly in the section", "manual", [], [])] },
      { id: "9", title: "An empty section", parts: [{ id: "9_ov", name: "overview", prose: "Synthetic text of a section without rules." }] },
    ],
    "back-matter": { resources: [
      res("p-l1s", "Level 1 - Server", [mark("xccdf_org.cisecurity.benchmarks_profile_Level_1_-_Server")]),
      res("p-l2w", "Level 2 \\ Workstation", [mark("xccdf_org.cisecurity.benchmarks_profile_Level_2_-_Workstation")]),
      res("s-8-4.1", "4.1", [{ name: "version", class: "CIS_Controls", value: "8" }, mark("4.1")]),
      res("s-8-12", "12", [{ name: "version", class: "CIS_Controls", value: "8" }, mark("12")]),
      res("s-7-9.2", "9.2", [{ name: "version", class: "CIS_Controls", value: "7" }, mark("9.2")]),
      res("s-bad", "no number", [{ name: "version", class: "CIS_Controls", value: "8" }]),
      res("d-1", "A synthetic manual page", [], "https://example.org/sshd_config"),
    ] } } };
}
