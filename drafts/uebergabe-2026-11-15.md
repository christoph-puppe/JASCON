# Übergabe, 2026-11-15

Für die nächste Session an diesem Repository. Geschrieben am Ende der
Session, die den Backlog bis kurz vor den Tag `v2.0.0` gebracht hat.
Was hier steht, ist gemessen oder im Repository nachzulesen; wo es nur
gelesen oder beobachtet ist, steht das dabei.

## 1. Stand

- **Branch:** `claude/sleepy-planck-g6w3h3`. Alles liegt dort und ist
  gepusht. Der Branch ist 228 Commits vor `main` und 0 dahinter
  (gemessen in diesem Klon). Es gibt keinen Pull Request und keinen
  Tag.
- **Letzter Commit vor dieser Datei:** `625f7b25`. Der CI-Lauf dazu
  (Workflow „Validators", Lauf 118) ist in allen vier Jobs grün:
  Python-Referenz, PowerShell-Twin unter Windows PowerShell 5.1, App,
  Browser-Tests.
- **Zahlen:** 800 Vektoren in 18 Familien (jcs 22, modality 21,
  parameter 22, tailoring 19, attestation 32, facet 29, reference 56,
  lifecycle 58, tier 10, dsse 5, composition 11, conditional 8, risk 73,
  kernel 97, scale 18, check 205, advice 74, author 40). Referenz, Twin
  und App bestehen alle. Sechs Ledger: 214.455 Werte, 0 verloren,
  0 ungeklärt. Vier OSCAL-Exporte: 4.467 Objekte hin und zurück.
- **Versionen:** Spezifikation `drafts/jascon-specification-2.0.0-rc.4.md`
  (kein neuer Kandidat geschnitten; die Datei behält ihren Namen, bis
  der Autor den nächsten benennt). Kernel-Schema
  `jascon/schemas/jascon-2.0.0.schema.json`. App Build 0.9.23. Reader
  1.21.0. Grundschutz++-Konverter v0.6 auf dem BSI-Katalog vom
  2026-10-29, `gspp-taxonomy` 1.1.0.

## 2. Was offen ist

Nichts davon ist ohne das Wort des Autors zu beginnen.

| Was | Stand |
|---|---|
| Tag `v2.0.0` | wartet auf das Go des Autors; laut Spezifikation IV.9 blockiert nichts |
| E16, Aufräumen | eigene, große Aufgabe; Umfang ist erst vorzuschlagen (`drafts/phase-e/entscheidungen-phase-e.md`, „E16"). Löschen erst nach einem Ja |
| #62 | ein `http-api`-Collector hat kein erklärtes Format; für nach dem Tag vorgeschlagen |
| #71 | offen sind die Punkte 1 bis 4 und 6 bis 12 (App und Reader); gebaut sind 5, 13, 14 |
| #79 | offen sind die Punkte 1, 4, 6, 7, 8 (Konverter-Reste); gebaut 3, 5; Punkt 2 war schon erledigt |
| #91 | offen sind die Punkte 3, 5, 6; „bei der nächsten Änderung, die die Stelle berührt" |

Der Backlog ist `drafts/jascon-v0.6-spec-feedback-backlog.md`. Sein
Kopf hat je Runde einen Absatz, der mit „Open now:" endet; der letzte
nennt #62, #71, #79, #91.

### Beobachtet und nirgends abgelegt

Diese Punkte sind beim Bauen aufgefallen und nicht geprüft. Sie stehen
weder im Backlog noch sind sie dem Autor vorgelegt.

- Reader: Der aufgelöste Geltungsbereich behält zurückgezogene
  Anforderungen, die ein Set noch aufführt. Die Referenz lässt sie in
  ihrer Zählung für risk-coverage weg. In beiden Codes gelesen, nicht
  gemessen. Ob es für ein aufgelöstes Paket ein Fehler ist, ist offen.
- Reader: Eine Operation auf eine Anforderung, die ein Ausschluss aus
  dem Geltungsbereich nimmt, erscheint in der Vorschau vermutlich
  weiter als „modified". Aus dem Code geschlossen, nicht gemessen.
- `website/facts.json` ist an `385f0fdf` gemessen. Danach bekam der
  Kopf des Twins zwei Zeilen mehr; die Zeilenzahl dort hinkt nach. Die
  veröffentlichte Seite misst im Workflow selbst.

### Bekannt und mit Absicht so gelassen

- CHECK-12 liest ein `set-parameter` ohne `statement-id` in allen drei
  Validatoren weiter als gebunden. Seit OPERATION-1 fällt ein solches
  Bundle vorher durch. Steht im Register.
- Die CIS Controls werden vom Workflow nicht konvertiert.
- Fünf Korpora haben kein Ledger, weil ihre Quellen nicht im Repository
  sind (C3A, C5, CyFun, CIS Benchmark, CIS Controls).

## 3. Was diese Session zuletzt gebaut hat

Ausführlich im Register (`drafts/jascon-decision-rationale-register.md`,
die letzten Abschnitte) und in `drafts/phase-e/entscheidungen-phase-e.md`
mit den Worten des Autors.

- #82: FRAGMENT-1, ein Bericht, was Verweise der Form `#id` benennen.
- #93: WITHDRAWN-1, ein Fehler: Ein Objekt in Kraft stützt sich nicht
  auf ein zurückgezogenes.
- #94, #89, #95: Grundschutz++ auf dem Katalog vom 2026-10-29, ein
  typisiertes Taxonomie-Schema, Pfadkarte gegen Ledger in allen sechs
  Konvertern.
- #72: Jede Zahl einer Pin-Version ist höchstens 2^53 − 1.
- #79 (3), (5): Der CR26-Konverter bricht bei einem unbekannten
  Verbindlichkeitswort ab; `--out` ist Pflicht.
- #71 (5), (13), (14): Der Reader nennt, was er beim Auflösen nicht
  anwendet, und schreibt dann kein Paket; Set-Ausschluss nach D13.
- #96: OPERATION-1, ein Fehler: `set-modality`, `set-parameter` und
  `replace-prose` nennen ihre Aussage, und ein `set-parameter` nennt
  einen deklarierten Parameter. Gebaut für alle drei Arten; dem Autor
  waren zwei Fälle vorgelegt. Das steht im letzten Bericht an ihn, eine
  Antwort darauf gab es nicht mehr.

## 4. Wie der Autor arbeiten will

- **Nur tun, was gesagt ist.** Keine angenommenen Aufgaben. Erst
  entscheiden lassen, dann bauen. Bei einer Frage: Vorschlag mit
  Gründen, dafür und dagegen.
- **Befunde nicht still beheben.** Was beim Bauen auffällt, wird
  gemessen, im Backlog abgelegt und dem Autor vorgelegt.
- **Kurz berichten, auf Deutsch, Ergebnis zuerst.** Der Autor prüft die
  Antworten mit Gemini und Grok gegen.
- **Sätze erst nach der Messung schreiben.** Jede Aussage ist als
  gemessen, gelesen oder geschlossen gekennzeichnet. Ein fehlender
  freiwilliger Wert ist eine Berichtszeile, nie eine Ablehnung.
- **Absichtliche Fehler nur für neue Logik:** die Stelle in einer Kopie
  brechen und zeigen, dass ein Vektor oder Test rot wird.
- **Texte einmal am Ende einer Runde**, nicht nach jedem Schritt.
- **Keine parallelen Agenten auf gekoppelten Dateien.** Kleines selbst
  machen; Agenten nur für große, abgegrenzte Aufgaben, dann in einem
  Worktree, mit Auftrag in einer Datei und kurzem Bericht.
- **Der Autor** wird ohne Pronomen genannt („der Autor"), auf Englisch
  „the author".
- Jede Regel gilt in Referenz, Twin und App gleich, und im Reader, wo er
  sie trägt. Zahlen stimmen in jeder Sprache der Website.

## 5. Regeln der Umgebung

- Nur auf den zugewiesenen Branch pushen. Eine neue Session bekommt
  womöglich einen neuen Branch-Namen: dann zuerst
  `claude/sleepy-planck-g6w3h3` holen und darauf aufsetzen, sonst fehlt
  die Arbeit von 228 Commits. Kein Pull Request ohne Auftrag. Kein
  Force-Push.
- Ein Stop-Hook verlangt vor jedem Ende eines Zugs: alles committet und
  gepusht.
- Jeder Commit endet mit den zwei Zeilen, die die Session vorgibt
  (`Co-Authored-By` und `Claude-Session`). Sonst steht kein
  Modellname in einem Artefakt.
- GitHub nur über die MCP-Werkzeuge und nur für dieses Repository.
  `raw.githubusercontent.com` ist per HTTPS erreichbar; andere
  Repositories lassen sich nicht anbinden.
- Nicht in ein Worktree wechseln (`git -C` nehmen), das
  Arbeitsverzeichnis bleibt die Wurzel des Repositorys. Nie pauschal
  unter `/tmp` aufräumen.
- `sources/` ist nicht eingecheckt. Vor Konverter-Läufen:
  `bash .github/scripts/fetch-pinned-sources.sh .github/oscal-catalog-schema.sha256`

## 6. Eine Runde, wie sie hier gelaufen ist

1. Messen, was heute gilt, an Kopien außerhalb des Repositorys.
2. Regel in `jascon/scripts/validate_core.py`, Vektoren unter
   `jascon/conformance/`, absichtliche Fehler.
3. Twin `jascon/scripts/validate_core.ps1` (nur ASCII; kein Operator
   vergleicht zwei Zeichenketten), App `jascon-app/jascon-rules.js` mit
   Build-Nummer in `jascon-core.js` und `readme.md`, Reader
   `one-page-apps/jascon-reader.html` mit `READER_VERSION`.
4. Texte: Spezifikation (Banner, die Entscheidung, IV.5b, IV.6, IV.9),
   Handbuch unter `jascon/references/`, `README.md`, `jascon/SKILL.md`,
   Kopf des Twins, `jascon-app/PROGRESS.md`; Backlog, Register,
   `entscheidungen-phase-e.md`, `pre-2.0.0-fix-plan.md`,
   `docs-to-change.md`.
5. Commits in dieser Folge: Code, Reader, Texte; dann
   `website/facts.json` und `SKILL_jascon.zip`, die beide den
   committeten Stand lesen.
6. Push, CI-Lauf prüfen.

### Befehle

```bash
python3 jascon/scripts/validate_core.py --as-of 2026-11-15      # Referenz: Vektoren und alle Bundles
node --test "jascon-app/tests/*.test.mjs"                       # App; node meldet rund 190 s, im Hintergrund starten
node --test jascon-app/tests/pages.test.mjs "one-page-apps/tests/*.test.mjs"   # Browser; node meldet 210 bis 255 s
python3 jascon/scripts/test_convert_cr26.py                     # und test_convert_{ifa,ism,bsi,csf,nist}_ledger.py, test_oscal_conv_lib.py
node jascon-app/tools/gen-schema.mjs --check
node jascon-app/tools/gen-docs.mjs --check
node jascon-app/tools/check-i18n.mjs
node one-page-apps/tools/sync-inlined.mjs --check               # ohne --check: Kopie im Pack-Builder nachziehen
python3 .github/scripts/pinned-schemas.py
python3 website/build.py --measure                              # schreibt website/facts.json am aktuellen Commit
python3 drafts/cp-advice-1/build_skill_zip.py --write           # baut SKILL_jascon.zip aus HEAD; ohne --write: Prüfung
python3 drafts/phase-d/attest_example.py --check
```

Die Schritte des Python-Jobs stehen in `.github/workflows/validators.yml`
und lassen sich lokal in derselben Folge ausführen.

## 7. Was mit der Session verloren geht

Der Arbeitsordner der Session wird gelöscht. Darin lagen Hilfen, die
nicht im Repository stehen.

- **PowerShell 7.4.6 für Linux**, entpackt, als Ersatz für Windows
  PowerShell 5.1. Wie es beschafft wurde, weiß ich nicht mehr. Ohne es
  bleibt der Windows-Job der CI der einzige Lauf des Twins; er ist ohnehin
  der maßgebliche.
- **Twin unter Linux:** Der Twin lädt `System.Web.Extensions`, das es
  nur im .NET Framework gibt. Der Lauf ersetzt diese eine Zeile durch
  einen Ersatz (unten) und startet eine Kopie aus einem Spiegel-Baum
  mit Verweisen auf `jascon/{conformance,examples,example-packs,references,schemas}`
  und `converted_examples`:

  ```bash
  sed "s|^Add-Type -AssemblyName System.Web.Extensions$|. '<Pfad>/shim.ps1'|" jascon/scripts/validate_core.ps1 > <Spiegel>/jascon/scripts/validate_core.ps1
  pwsh -NoLogo -NoProfile -File <Spiegel>/jascon/scripts/validate_core.ps1 -AsOf 2026-11-15      # mit -VectorsOnly: nur die Vektoren
  pwsh -NoLogo -NoProfile -File .github/scripts/lint-twin.ps1
  ```

- **Absichtliche Fehler:** ein Spiegel-Baum wie oben, `jascon/scripts`
  kopiert, eine Stelle ersetzt (die alte Stelle muss genau einmal
  vorkommen), Referenz oder Test darauf laufen lassen. Achtung: Ein
  Spiegel, der `converted_examples` als Verweis enthält, schreibt bei
  einem Konverter-Mutanten in den echten Ordner; danach `git status`
  prüfen.
- **Messkopien eines Bundles:** Ordner kopieren, ein Objekt ändern, im
  Manifest `package-digest` (SHA-256 der Bytes) und `semantic-digest`
  (SHA-256 der kanonischen Form ohne `annotations`) neu eintragen.
  `validate_core.py` lässt sich nicht importieren: es läuft beim Import
  los.
- **Bildschirmfoto des Readers** für `docs/img/reader-assess.png`
  (unten). Es zeigt die Versionsnummer, also nach jeder neuen
  Reader-Version neu aufnehmen.

### Anhang A: Ersatz für `JavaScriptSerializer` (`shim.ps1`)

```powershell
# Stand-in for System.Web.Script.Serialization.JavaScriptSerializer, which
# exists only in the .NET Framework. Same result types as the original:
# Dictionary<string,object>, object[], string, bool, int / long / decimal.
Add-Type -TypeDefinition @'
using System; using System.Collections.Generic; using System.Globalization; using System.Text.Json;
namespace System.Web.Script.Serialization {
  public class JavaScriptSerializer {
    public int MaxJsonLength { get; set; }
    public int RecursionLimit { get; set; }
    public object DeserializeObject(string s) {
      var opt = new JsonDocumentOptions { MaxDepth = 1024 };
      using (var d = JsonDocument.Parse(s, opt)) { return Conv(d.RootElement); }
    }
    static object Conv(JsonElement e) {
      switch (e.ValueKind) {
        case JsonValueKind.Object: {
          var m = new Dictionary<string, object>(StringComparer.Ordinal);
          foreach (var p in e.EnumerateObject()) m[p.Name] = Conv(p.Value);
          return m; }
        case JsonValueKind.Array: {
          var l = new List<object>();
          foreach (var x in e.EnumerateArray()) l.Add(Conv(x));
          return l.ToArray(); }
        case JsonValueKind.String: return e.GetString();
        case JsonValueKind.True: return true;
        case JsonValueKind.False: return false;
        case JsonValueKind.Null: return null;
        default: {
          string raw = e.GetRawText();
          if (raw.IndexOfAny(new[] { '.', 'e', 'E' }) < 0) {
            int i; long l; decimal m;
            if (int.TryParse(raw, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out i)) return i;
            if (long.TryParse(raw, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out l)) return l;
            if (decimal.TryParse(raw, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out m)) return m;
          }
          decimal dm;
          if (decimal.TryParse(raw, NumberStyles.Float, CultureInfo.InvariantCulture, out dm)) return dm;
          return double.Parse(raw, CultureInfo.InvariantCulture); }
      }
    }
  }
}
'@
```

### Anhang B: Bildschirmfoto (`shot2.mjs`)

Aufruf: `node shot2.mjs <Ziel.png> 2 stage:assess 1`

```js
// The README's own way: `python -m http.server` in the repository root, then the README's link.
import { createRequire } from "node:module"; const { chromium } = createRequire(import.meta.url)("playwright");
import { spawn } from "node:child_process"; import net from "node:net";
const out = process.argv[2], dsf = Number(process.argv[3] || 1), view = process.argv[4] || "stage:assess", scroll = Number(process.argv[5] || 0);
const port = await new Promise(r => { const s = net.createServer().listen(0, "127.0.0.1", () => { const p = s.address().port; s.close(() => r(p)); }); });
const py = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"], { cwd: "/home/user/JASCON", stdio: "ignore" });
await new Promise(r => setTimeout(r, 1200));
const base = `http://127.0.0.1:${port}/`;
const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: dsf });
const page = await ctx.newPage(); const errs = []; page.on("pageerror", e => errs.push(String(e)));
await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.fulfill({ status: 200, contentType: "text/css", body: "" }));
await page.goto(base + `one-page-apps/jascon-reader.html#load=../converted_examples/US.IFA-GoodRead/ifa-core-bundle/&view=${view}`);
await page.waitForFunction(() => document.body.dataset.binds === "done", null, { timeout: 30000 });
await page.waitForTimeout(800);
if (scroll) { await page.evaluate(() => { const els = [...document.querySelectorAll("main *, #main *, .content *")].filter(e => e.children.length === 0 && /FULL MATCH/.test(e.textContent)); (els[0] || document.body).scrollIntoView({ block: "center" }); }); await page.waitForTimeout(400); }
await page.screenshot({ path: out });
const info = await page.evaluate(() => ({ pill: document.getElementById("pill-bundle").textContent, version: document.getElementById("pill-version").textContent,
  heads: [...document.querySelectorAll("h2, h3, .sec-title, .stage-title")].map(e => e.textContent.trim()).filter(Boolean).slice(0, 14),
  att: document.body.innerText.includes("FULL MATCH"), risk1: document.body.innerText.includes("IFA-GOODREAD-RISK-1"), h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth }));
console.log(JSON.stringify(info), "errors:", errs.length);
await b.close(); py.kill();
```
