# Phase E: offene Entscheidungen, mit Vorschlag

Stand 2026-11-14, Commit 430cf15a (CI-Lauf 93 grün in allen vier Jobs).
Arbeitspapier für die Entscheidungssitzung; die Ergebnisse gehen danach
ins Register (englisch).

## Vorgehen (vom Autor entschieden, 2026-11-14)

1. Erst entscheiden, dann bauen.
2. Keine parallelen Agenten auf gekoppelten Artefakten; sequenziell,
   Kleines selbst; Agenten nur für große, isolierte Aufgaben, mit Budget,
   ohne Extras, mit kurzem Bericht.
3. Verifikation nach Risiko: Defekt-Läufe nur für neue Logik, keine
   Bestätigungs-Agenten, eine unabhängige Zählung.
4. Texte (README, Spezifikation, Handbuch, Website) einmal am Ende,
   anhand von `docs-to-change.md`.
5. Die JavaScript-Presets bleiben ergebnisgleich mit den
   Python-Konvertern. Zahlen stimmen in jeder Sprache und werden bei
   jeder Änderung nachgezogen. Der Ledger darf bei großen Korpora gröber
   werden (wie, siehe E12).
6. Kürzer kommunizieren; bei Fragen einen Vorschlag machen, mit
   Begründung und Pro/Contra.

Antwortformat: je Punkt „ja“, „nein“ oder eine andere Wahl, z. B.
„E1 ja, E2 B, E3 ja ...“.

---

## Block 1: Was ist Inhalt? (löst Konverter-Änderungen aus)

### E1. Zurückgezogene Elemente: eigenes Objekt statt Abstammungs-Eintrag

**Stand (gemessen).** CSF: 87 zurückgezogene Elemente mit Nachfolger
sind kein Objekt, nur ein `replaces`-Eintrag beim Nachfolger plus eine
Annotation. SP 800-53: 180. Die 335 `replaces`-Verweise (135 CSF, 200
SP 800-53) zeigen auf kein Objekt des Bundles. Die Statuswörter
`withdrawn` (180) und die sort-ids (87) sind deklarierte Drops; Label,
Titel und Prosa stehen in einer Annotation, die der semantische Digest
auslässt. Zurückgezogene Elemente *ohne* Nachfolger sind schon Objekte
mit `lifecycle: withdrawn` (cp-10.3, sc-19, vier CSF-Kategorien).

**Vorschlag: ja.** Jedes zurückgezogene Element wird ein Objekt mit
`lifecycle: withdrawn`; der Nachfolger behält `replaces`.

- **Pro:** `lifecycle: withdrawn` ist im Kernel genau dafür da. Das
  Statuswort wird zum Lebenszyklus, also braucht es keine neue Regel-
  klasse „Wert, der die Darstellung entscheidet“. sort-id, Label, Titel
  und Prosa stehen im Objekt und damit im Digest. Alle 335 Verweise
  lösen auf. Ein Verfahren statt zwei.
- **Contra:** 267 Objekte mehr. Der Kernel verlangt ein Statement, siehe
  E2. Abkehr von der „Tombstone-Inversion“ des Gate-3-Zensus; Texte
  dazu ändern sich. Arbeit: CSF- und SP-800-53-Konverter,
  SP-800-53-Preset, Tests.

### E2. Zurückgezogene Anforderung ohne Statement

**Stand.** Der Kernel verlangt mindestens ein Statement mit Modalität
und verpflichteter Partei. cp-10.3 und sc-19 bekommen heute
`unspecified` und die Default-Partei des Konverters, also einen
erfundenen Wert. Mit E1 beträfe das 261 Anforderungen (79 CSF-Subkategorien, 180 SP-800-53-Controls, cp-10.3, sc-19); die 8 CSF-Kategorien würden Sets, die kein Statement brauchen.

**Vorschlag: A.**

- **A. Kernel ändern:** Bei `lifecycle: withdrawn` darf `statements`
  leer sein. Pro: nichts Erfundenes. Contra: Schema-Änderung in drei
  Validatoren, neue Vektoren, Spezifikation D3/D9; vorher prüfe ich, ob
  alle drei die Bedingung (if/then) können.
- **B. So lassen:** erfundenes Statement. Pro: keine Kernel-Änderung.
  Contra: Modalität und Partei ohne Quelle, auf jedem zurückgezogenen
  Objekt.

### E3. Klasse A: die UUID des Quelldokuments

**Stand.** ISM 1, CSF 1, Grundschutz++ 1, SP 800-53 5 (Katalog und
vier Profile), dazu die Dokument-UUIDs unter den 84 von IFA.

**Vorschlag: ja, übernehmen**, in den compat-`metadata` des Wurzel-Sets,
wo die übrigen Metadaten schon stehen.

- **Pro:** wenige Werte; sie identifizieren die Fassung der Quelle; die
  Regel „nie Inhalt verwerfen“ gilt ohne Ausnahme.
- **Contra:** geringer praktischer Nutzen, weil `SOURCES.sha256` die
  Quelle schon per SHA-256 pinnt.

### E4. Klasse B: Back-Matter-Ressourcen, auf die kein Control verweist

**Stand.** CSF 7 Werte, Grundschutz++ 5, SP-800-53-Profile 36 (mit den
vier `imports[].href`), IFA 57. ISM und der SP-800-53-Katalog tragen
ihre Ressourcen schon vollständig.

**Vorschlag: ja, übernehmen**, in der Form der Quelle im
references-Facet des Wurzel- bzw. Baseline-Sets, wie ISM.

- **Pro:** Die schon übernommenen Metadaten-Links zeigen sonst ins
  Leere. Alle Konverter verfahren gleich.
- **Contra:** CSF und Grundschutz++ müssen ein references-Facet pinnen;
  die App-Presets ziehen nach.

### E5. Die IFA-Klassen vom 2026-11-13 (Klasse C)

**Vorschlag, je Klasse:**

| Klasse | Werte | Vorschlag |
|---|---:|---|
| Revisionsgeschichte | 56 | übernehmen (compat `metadata`) |
| Verzeichnis der Parteien und Rollen | 56 | übernehmen (compat `metadata`) |
| UUIDs von Quellelementen | 84 | übernehmen, wo das Element ein Objekt wird (compat); Dokument-UUIDs nach E3 |
| Links auf andere Serialisierungen, Importe | 57 | übernehmen (nach E4) |
| Typ-Tags (`subjects[].type` …) | 11 | kein Inhalt per geprüfter Regel „rebuilt“: Typ = Art des Objekts, auf das der Verweis auflöst |
| eigener Komponenten-Eintrag des nutzenden Plans | 18 | gleich dem des Anbieters: geprüfte Dublette (`same()`); sonst übernehmen |
| Verweis auf eine Partei ohne Namen | 8 | übernehmen (compat) |
| früherer Stand eines Risikos (AR) | 3 | übernehmen (compat am Risk) |
| drei Quellfehler (Verweise ins Leere) | 3 | wörtlich übernehmen (compat), im Bericht als Quellfehler genannt |

- **Pro:** Die Regel gilt auch für IFA; IFA ist klein (296 Werte).
- **Contra:** Der compat-Facet wächst; einige UUIDs nützen niemandem.

### E6. CR26: Änderungshistorie und Ablaufdiagramm

**Stand.** Historie 957 Werte in 475 Einträgen (ein CTL-Eintrag wird
schon getragen), ein Ablaufdiagramm mit 35 Werten. D17 erklärt
Prozessabläufe für „out of scope“.

**Vorschlag: ja, übernehmen**: die Historie je Eintrag im narrative-Facet,
das Diagramm auf dem Familien-Set. D17 wird dazu geändert.

- **Pro:** Regel; Konsistenz mit dem einen Eintrag, der schon getragen
  wird.
- **Contra:** rund 1.000 Werte mehr im Bundle; D17 ändert sich.

### E7. SP 800-53: drei Drucklabels `a.` bei SI-2(7)

**Vorschlag: ja, übernehmen.** Die Regel ergibt `(a)`, also ist der Wert
nicht rekonstruierbar. Kein nennenswertes Contra.

---

## Block 2: Lebenszyklus ohne Quellwort

### E8. `active`, wo die Quelle keinen Status nennt

**Stand.** ISM 1.731, Grundschutz++ 1.287, CSF 135, SP 800-53 1.039,
CR26 14 Objekte. Der Kernel verlangt einen Lebenszyklus.

**Vorschlag: A.**

- **A. Benannter Konverter-Default:** `active`, im Bericht als Default
  des Konverters genannt, nach dem Muster der verpflichteten Partei
  (#74). Pro: keine Kernel-Änderung; Muster existiert; ein
  veröffentlichter Katalog gilt. Contra: ein Wert ohne Quellwort,
  allerdings erklärt.
- **B. Kernel ändern** (Lebenszyklus optional oder Wert `unstated`).
  Pro: nichts Erfundenes. Contra: drei Validatoren, Vektoren,
  Spezifikation; jedes Werkzeug muss „unstated“ deuten.

### E9. CR26: `placeholder` → `draft`

**Stand.** Familie AGU: 28 Objekte `draft`. Ihre Effektivität sagt
`required` ab einem Datum; laut Handbuch darf ein Entwurf nicht zitiert
werden; sieben aktive Sets enthalten AGUs Entwurfs-Sets.

**Vorschlag: bei `draft` bleiben**, Quellwort daneben (wie jetzt); den
Widerspruch im Bericht benennen. Ein Validator-Hinweis „aktives Set mit
Entwurfs-Mitglied“ kommt in den Backlog (nach dem Tag).

- **Pro:** „placeholder“ heißt nicht fertig, das ist `draft`.
- **Contra:** steht gegen die Effektivitätsangabe derselben Quelle.

---

## Block 3: Kernel und Facets

### E10. Der compat-Facet `oscal-1x` 1.0.0 hat vier verschiedene Schemas

**Stand (gemessen).** ISM, Grundschutz++, CSF und SP 800-53 pinnen
dieselbe Kennung und Version mit verschiedenen geschlossenen Schemas.
Folge in der App: Ein Profil, das in ein Grundschutz++-Set importiert
wird, verliert seine merge-Direktive.

**Vorschlag: ja, vereinheitlichen.** Ein Schema (Vereinigung aller
Member), einmal im Repository, Version 1.1.0, gepinnt von allen vier
Konvertern und beiden Presets.

- **Pro:** eine Kennung mit Version bedeutet ein Schema, sonst verliert
  der Pin seinen Sinn; das App-Problem verschwindet.
- **Contra:** vier Bundles und Exporte neu, die App zieht nach;
  mechanisch.

### E11. Was heute im compat- oder Konverter-Facet steht

Dokument-Metadaten; eigene Revision und Änderungsdatum (ISM 2.202);
Ressourcen, auf die Texte verweisen; assessment-for (3.707); Label eines
Statements (1.122); zweites Parameter-Label (1.458); alternative
Parameter-ID (221); risk-party (125); was ein Set darstellt;
Alias-Schemata; Brüche als Text; Statuswort der Quelle; eine Provenance
je Manifest.

**Vorschlag: für 2.0.0 nichts am Kernel ändern** (außer E2, falls
gewählt). Alles bleibt getragen, wo es steht, also ist Regel 3 erfüllt.
Jeder Befund kommt mit seinen Zahlen in den Backlog, als Kandidat nach
der Promotionsregel D22.

- **Pro:** keine neue Umbaurunde vor dem Tag.
- **Contra:** viel Inhalt in einem Facet ohne festgelegte Bedeutung.

### E12. Gröberer Ledger für große Korpora: wie grob?

**Stand.** Der Ledger rechnet pro Wert (SP 800-53: 3 Sekunden). Das
committete Protokoll ist schon pro Pfad (118 kB statt 741 kB). Teuer
war nicht die Laufzeit, sondern dass jede Ecke jeder Quelle eine Regel
brauchte und Agenten Formen abdeckten, die keine gepinnte Quelle hat.

**Vorschlag: A.**

- **A. Mechanik bleibt, der Aufwand wird gröber.** Für Korpora über rund
  10.000 Werte wird nur gegen die gepinnte Quelle getestet, nicht mit
  erfundenen Katalogen, die jede Ecke abdecken. Eine neue Form wird erst
  behandelt, wenn eine echte Quelle sie zeigt; bis dahin beendet das
  Gate den Lauf mit 1, also geht nichts still verloren. Pro: kein
  Umbau, das Gate bleibt. Contra: Das Protokoll wird nicht kleiner, als
  es ist.
- **B. Umbau auf Pfad-Ebene** (Werte je Pfad als Menge vergleichen).
  Pro: weniger Verdrahtung im Konverter. Contra: verliert genau, wofür
  der Ledger gebaut wurde (#33: gleicher Text an anderer Stelle verdeckt
  einen Verlust), und kostet eine weitere Umbaurunde.

---

## Block 4: Texte

### E13. Das Argument für die Statement-Ebene

**Gemessen.** Mehrere Statements je Anforderung gibt es nur bei
SP 800-53 (284 von 1.016) und IFA (2 von 2). In keinem Korpus
unterscheiden sich Modalität oder Partei innerhalb einer Anforderung.
IFA adressiert 41-mal ein einzelnes Statement; SP 800-53A hat 3.707
assessment-for-Verweise auf Statements.

**Vorschlag: neu begründen mit Adressierbarkeit.** Die Items a., b., c.
von SP 800-53 werden einzeln umgesetzt (IFA) und einzeln geprüft
(SP 800-53A). „347 Pseudo-Controls“ wird gestrichen. Offen gesagt wird,
dass kein Korpus Modalität oder Partei innerhalb einer Anforderung
mischt: Dass beide am Statement stehen, ist eine Entwurfsentscheidung
ohne Korpus-Beleg.

- **Pro:** belegt und ehrlich.
- **Contra:** Die Erzählung von D9 wird schwächer; Handbuch Kapitel
  1–5 und 14, Anhänge A und E, Spezifikation, Website in fünf Sprachen.

---

## Block 5: Kleinere Punkte

### E14. Zwei Konverter-Fehler, die die App-Agenten fanden

`convert_bsi.py` bei leerem Parameter-Label und `convert_nist.py` bei
einem reference-Link auf eine Ressource ohne Link enden mit 1. Keine
gepinnte Quelle hat diese Formen. Die App-Tests akzeptieren genau diese
Fehlschläge.

**Vorschlag: beheben** (klein, ich selbst, mit Test), und die Ausnahme
in den App-Tests entfernen.

- **Pro:** Kein Test toleriert mehr einen bekannten Fehler.
- **Contra:** Nach E12 A würde man warten, bis eine echte Quelle die
  Form zeigt. Hier ist der Fehler aber schon bekannt und die Tests
  bilden ihn ab.

### E15. Reader-Befunde

Das Export-Log meldet „passes validate_core.py“, wo die Referenz
scheitert. Außerdem hält der Reader `facets` nicht an die Methoden-Regel.

**Vorschlag:** das falsche „passes“ jetzt beheben, weil die Seite etwas
Falsches über die Referenz behauptet; die `facets`-Regel in den Backlog.

### E16. Aufräumen

Die alten Agenten-Worktrees und -Branches sind lokal und schon gemerged;
`SKILL_jascon.zip` ist veraltet.

**Vorschlag:** Worktrees und Branches nach Phase E löschen, das Archiv
mit den Texten am Ende neu bauen. Löschen geschieht erst nach deinem Ja.

---

## Reihenfolge danach

Konverter-Änderungen aus E1–E7, E10 und E14: ein Durchgang je Konverter,
jeweils mit seinem Preset. Danach IFA- und CR26-Läufe neu. Dann einmal
alle Texte nach `docs-to-change.md`, in allen Sprachen. Zuletzt Register,
Backlog und Archiv.

---

## Entscheidungen des Autors (2026-11-14)

Wörtlich, und wie ich sie lese. Was noch eine Rückfrage braucht, steht
darunter.

| | Antwort des Autors | Gelesen als |
|---|---|---|
| E1 | „ja, tools müssten dann sehr alte irgndwann entfernen, weil es sonst unübersichtlich wird“ | Jedes zurückgezogene Element wird ein Objekt mit `lifecycle: withdrawn`. Dazu ein Backlog-Punkt: Werkzeuge brauchen einen Weg, sehr alte zurückgezogene Objekte auszublenden oder zu entfernen. |
| E2 | „statement bleibt“ | B: keine Kernel-Änderung; eine zurückgezogene Anforderung trägt ein Statement. Folge siehe Rückfrage R2. |
| E3 | „übernehmen“ | Die UUID des Quelldokuments wird getragen. |
| E4 | „orphaned elemente braucht niemand“ | Verwaiste Back-Matter-Ressourcen werden nicht getragen. Was „verwaist“ genau heißt: Rückfrage R1. |
| E5 | „zustimmung“ | Die IFA-Tabelle wie vorgeschlagen; die Zeile „Links … (nach E4)“ folgt R1. |
| E6 | „zustimmung“ | CR26: Änderungshistorie und Ablaufdiagramm werden getragen; D17 wird geändert. |
| E7 | „zustimmung“ | Die drei Drucklabels von SI-2(7) werden getragen. |
| E8 | „zustimmung“ | `active` ohne Quellwort ist ein benannter Konverter-Default mit Berichtszeile. |
| E9 | „zustimmung, aber auch draft darf ausgefüllt werden, freiwilliug geht alles -> handbuch anpassen“ | `placeholder` bleibt `draft`. Das Handbuch (ch03 §3.6: ein Entwurf „must not be cited by anything claiming conformance“) wird geändert: Auch ein Entwurf darf freiwillig umgesetzt und bewertet werden. Gemessen: Kein Validator verbietet das heute; es ist nur ein Satz im Handbuch. |
| E10 | „zustimmung“ | Ein gemeinsames compat-Schema, Version 1.1.0. |
| E11 | „Doch 2.0.09 ist alles zur Veränderung freigegeben, gut begründet. Daher alle befinde ins backlog“ | Für 2.0.0 darf sich auch der Kernel ändern, wenn es gut begründet ist. Jeder Befund wird ein Backlog-Punkt mit Zahlen und begründetem Vorschlag; gebaut wird ein Punkt erst nach Entscheidung. |
| E12 | „zustimmung“ | A: Die Ledger-Mechanik bleibt; große Korpora werden nur gegen die gepinnte Quelle getestet. |
| E13 | „stimmt, eine anforderung mit mehreren parteien sollte gehen, aber immer nur eine modalität“ | Das Argument wird mit Adressierbarkeit neu begründet. Zur Modalität: Rückfrage R3. |
| E14 | „zustimmung“ | Die zwei Konverter-Fehler werden behoben, die Ausnahmen in den App-Tests entfernt. |
| E15 | „1: fixen; 2 fixen“ | Beide Reader-Befunde werden behoben. |
| E16 | „ja, aufräumen wird ein großer Task“ | Aufräumen ist eine eigene, große Aufgabe nach Phase E; ihren Umfang schlage ich dann vor. |

### Rückfragen, mit Messung (alle gemessen am 2026-11-14)

**R1. Was heißt „verwaist“?** Gezählt in den Quelldateien, wer auf eine
Back-Matter-Ressource verweist:

| Quelle | Ressourcen | verwiesen aus Text / Link / Metadaten / Import | nichts verweist |
|---|---:|---|---:|
| ISM | 246 | Text 241, Metadaten 5 | 0 |
| CSF | 4 | Metadaten 3 | 1 |
| Grundschutz++ | 1 | Metadaten 1 | 0 |
| SP 800-53, Katalog | 201 | Link oder Text 169, Metadaten 9 | 23 |
| SP 800-53, vier Profile | je 1 | Import 1 | 0 |
| IFA, sieben Dokumente | 15 | Metadaten 8, Import 3, Link 2 | 2 |

**R2. Was sagt das Statement eines zurückgezogenen Controls?** Die 180
zurückgezogenen SP-800-53-Controls mit Nachfolger haben in der Quelle
keine Prosa, nur Links (`incorporated-into` 166, `moved-to` 34). Bei CSF
haben 79 der 87 eigene Prosa; die 8 ohne sind Kategorien und werden
Sets.

**R3. „Immer nur eine Modalität“.** Heute erlaubt der Kernel
verschiedene Modalitäten je Statement einer Anforderung. Das
Handbuch-Beispiel `req-konf-14-1.json` nutzt das (Betreiber `may`, Kunde
`should`), dazu 37 Fixtures in den Vektoren (risk 8, advice 29). In den
konvertierten Korpora mischt keine Anforderung Modalität oder Partei.
