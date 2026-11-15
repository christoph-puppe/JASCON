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

### Antworten auf die Rückfragen (Autor, 2026-11-14)

„R1 ja, R2 statement bleibt pflicht, R3 merhere modalitäten und mehrere
parteien, das bleibt , Plan go“

- **R1:** Verwaist ist, worauf im Dokument nichts verweist. Das wird
  nicht getragen, per geprüfter Regel „orphan“; alles andere wird in der
  Form der Quelle getragen.
- **R2:** Das Statement bleibt Pflicht. Für die 180 zurückgezogenen
  SP-800-53-Controls ohne eigene Prosa entsteht die Prosa per benannter
  Regel aus den Links der Quelle; Modalität `unspecified`, Partei der
  Konverter-Default.
- **R3:** Mehrere Modalitäten und mehrere Parteien je Anforderung
  bleiben, wie der Kernel sie heute erlaubt. Kein Backlog-Punkt dazu.
- **Plan:** freigegeben.

## Nach Phase E: Backlog #80 bis #92 (Autor, 2026-11-14)

Vorgelegt wurden #80 bis #85 je mit Vorschlag, Pro, Contra und meiner
Empfehlung (die Texte stehen in den Backlog-Zeilen). Zu #86 bis #92 die
Frage des Autors: „86 bis 92 kannst Du alleine machen, oder?“ Meine
Antwort: ja, bis auf eine Entscheidung in #91.

Die Worte des Autors:

„alle wie empfohlen, bis auf 81: Versionierung ist wichtig und gehört in
den Kernel, die Validatoren müssen dann angepasst werden“

„91: ja“

| Nr. | Entscheidung |
|---|---|
| 80 | Wie empfohlen. `provenance.sources[]` wird im Kernel-Schema typisiert, ein Eintrag je Quelldokument; `provenance` bleibt sonst offen. Der Rest der Dokument-Metadaten bleibt im compat-Facet `metadata`; kein neues Standard-Facet. |
| 81 | Nicht als Facet: Versionierung gehört in den Kernel, die Validatoren werden angepasst. Die Form ist offen (siehe unten). |
| 82 | Wie empfohlen. Ein Standard-Facet `references@1`. Für die Auflösungsregel (`#id` im Text) wird zuerst gezählt, ob ein Bundle Verweise ins Leere hat: bei 0 Fehler des Bundles, sonst Berichtszeile. |
| 83 | Wie empfohlen. `assessment-criteria` bekommt typisierte `objectives[]` mit `assessment-for` (Version 1.1.0); D10 hält ein `statement-id` in einem Payload wie einen `by-statement`-Schlüssel. |
| 84 | Wie empfohlen. `label` am Statement kommt in den Kernel (Entscheidung gegen D22, Tests 1 und 2). `aliases` am Parameter nicht; die 221 Parameter-uuids bleiben in compat. |
| 85 | Wie empfohlen. Kein Kernel-Feld `kind` am Set für 2.0.0. |
| 91 (2) | `author` ist eine Rolle, aus der der Konverter den Autor des Dokuments liest. |

### #81: was vor dem Bauen noch offen ist

Vorgelegt am selben Tag, noch ohne Antwort. Befund: Der Kernel hat
`version` an jedem Objekt, und das Handbuch (§3.3) sagt, jede Änderung
sei eine neue adressierbare Version. Die Konverter nutzen das nicht: alle
1.731 ISM-Objekte tragen die Ausgabe `2026.06.18` (gemessen), die eigene
Revision des Controls steht in compat (1.101 Controls, 14 verschiedene
Werte). Die Referenz rechnet schon auf `version`: beim Zusammensetzen
zweier Bundles ist gleiche id mit gleicher Version und anderem Digest ein
Fehler. D26, Entscheidung vom 2026-11-13, sagt: „The kernel keeps no log
inside an object, because a second history inside each version can
contradict the first.“

Vorschlag: (1) `version` ist die eigene Version des Objekts, wo die
Quelle eine nennt, sonst die Ausgabe; keine Schemaänderung. (2) Ein neues
optionales Kernel-Feld `history[]` an jedem Objekt, Einträge
`{date, comment?, ref?}`, `date` als Tag oder Monat, Teil des
semantischen Digests. (3) Schema und eine Regel „Einträge aufsteigend
nach Datum“ in allen drei Validatoren, mit Vektoren. Der Satz in D26 und
§3.3 des Handbuchs würden umgeschrieben; dafür braucht es das Ja des
Autors. Kleinere Alternative: nur (1), Monat und Historie in ein Facet.

### Was davon schon gebaut ist (2026-11-14)

Die vier Punkte, die an keiner dieser Entscheidungen hängen: #90 (der
Workflow führt den OSCAL-Export aus), #86 (DRAFT-1 in allen drei
Validatoren), #87 (Schalter für Zurückgezogene, App 0.9.18 und Reader
1.17.0), #92 (Reader 1.17.0; der App-Teil gemessen und nicht geändert).
Kernel, Standard-Facets und Konverter (#80 bis #84, mit #88, #89, #91)
warten auf die Antwort zu #81, damit jedes Bundle nur einmal neu entsteht.

### #81: die Antwort des Autors (2026-11-14)

„81: ja, so wie vorgeschlagen!“

Damit gilt: `version` ist die eigene Version des Objekts, wo die Quelle
eine nennt; `history[]` ist ein optionales Kernel-Feld an jedem Objekt;
die Validatoren halten Form und Reihenfolge. Der Satz in D26 fällt.

### Was beim Bauen anders kam als vorgelegt (alle am 2026-11-14)

Jeder Punkt ist eine Festlegung von mir, die der Autor so nicht gesehen
hat, oder ein Befund, der eine vorgelegte Annahme widerlegt.

1. **#82, die Regel für `#id`: nicht gebaut.** Vorgelegt war: erst
   zählen, bei 0 Verweisen ins Leere ein Fehler, sonst eine
   Berichtszeile. Die Zählung ergab etwas Drittes: `#id` meint in
   SP 800-53 in 422 von 540 Fällen keine Ressource, sondern ein Control,
   ein Statement oder einen Parameter. Eine Zeile „422 nennen keine
   Ressource“ wäre wahr und würde keinen Defekt benennen. Das Facet
   `references@1` ist gebaut, die Regel wartet auf eine Entscheidung
   (Backlog #82, mit Vorschlag).
2. **#81, Begriffe von CR26.** Ein Begriff ist dort kein Objekt, sondern
   ein Eintrag von terminology@1 auf dem Wurzel-Set. `history` gilt je
   Objekt. Die Historie der Begriffe bleibt im Facet des Konverters; die
   von 291 Regeln und Indikatoren (390 Einträge) steht im Kernel.
3. **#81, Reihenfolge.** CR26 führt den neuesten Eintrag zuerst (alle 94
   Objekte mit mehreren Einträgen). Der Konverter ordnet nach Datum,
   älteste zuerst, wie HISTORY-1 es verlangt.
4. **#81, Einzelheiten der Form.** `comment` ist ein Text mit
   Sprachschlüssel wie jede Prosa des Kernels; `ref` ist eine URI; zwei
   Einträge dürfen dasselbe Datum tragen; ein Monat steht vor seinen
   Tagen. Ein Datum, das weder Tag noch Monat ist, heißt DATE-6.
5. **#81, ISM.** Die Monatsregel liest `Mon-YY` (so drucken es alle
   1.101 Controls). Eine andere Form beendet den Lauf, statt einen Monat
   zu erfinden.
6. **#83, Standardbibliothek mit Versionen.** Nicht vorgelegt, aber
   nötig: Ein Deskriptor der Bibliothek ließ sich nicht ändern, ohne
   jedes Bundle durchfallen zu lassen, das ihn pinnt. Jetzt hält die
   Bibliothek Versionen (1.0.0 bleibt neben 1.1.0), ein Pin wird an der
   Version gemessen, die er nennt, ein ungepinnter Payload an der
   neuesten.
7. **#83, Adressformen.** „Das Control als Ganzes“ ist `requirement-ref`
   allein; der eine Verweis ins Leere steht als `href`, wie die Quelle
   ihn schreibt.
8. **#80, IFA.** IFA hat kein Set je Dokument. Seine Ressourcen und der
   Rest der Dokument-Metadaten bleiben in den sieben Einträgen von
   `provenance.sources`.
9. **compat-Schema 1.2.0.** `back-matter` und `history` sind keine
   Mitglieder mehr; die Einträge von `props` und `group-parts` sind
   typisiert (#91, 4).
10. **#89 nicht gebaut.** Die Prüfung der Bibliothek, dass die Pfadkarte
    den Ort nennt, den der Ledger fand, hätte drei Konverter umgebaut,
    die eine eigene haben, und drei bekommen, die keine haben. Offen.

## Vier Antworten des Autors nach der Kernel-Runde (2026-11-14, später am Tag)

Vorgelegt waren die vier offenen Punkte #82, #93, #94 und #89. Die
Antworten des Autors, wörtlich:

> #82 agreed
> #93 regel bauen
> #94 die alten daten sind egal, welches von beiden ist die aktuelle gemäß BSI  repo?
> #89 was ist das?

### #82: was `#id` benennt (FRAGMENT-1, ein Bericht)

Gebaut wie vorgeschlagen: D9 sagt, was `#id` benennen darf, und ein
Validator berichtet je Bundle, wie viele Verweise welche Art benennen
und welche nichts. Nichts schlägt dadurch fehl. Gemessen: SP 800-53 hat
541 solche Verweise, 118 auf eine Ressource, 348 auf ein Control, 73 auf
ein Statement, 1 auf einen Parameter und 1 ins Leere (`#ac-2_smt.a.5`
in SA-24, ein Fehler der Quelle); ISM 486, CSF 3, Grundschutz++ 1, alle
auf eine Ressource; IFA 1, auf das Quelldokument, aus dem ein Link kam.

### #93: Verweise auf ein zurückgezogenes Objekt (WITHDRAWN-1, ein Fehler)

Gebaut. Ein Validator sieht ein Bundle und kann einen Verweis nicht
datieren. „Neu“ sagt deshalb das Bundle: Eines, das vor dem Rückzug
gepackt wurde, führt das Objekt, wie es war, und bleibt gültig. In
einem, das es als zurückgezogen führt, darf sich nichts darauf stützen,
was selbst in Kraft ist.

### #94: welche Fassung von `gspp-taxonomy` 1.0.0 ist die des BSI

Das BSI veröffentlicht kein Facet-Schema. Es veröffentlicht den Katalog
und unter `documentation/namespaces/` je Eigenschaft eine Datei mit den
erlaubten Werten. Gemessen am Stand von `main`
(`control_layer/Grundschutz++/Grundschutz++-resolved_catalog.json`,
Katalogversion 2026-10-29, 1.000 Anforderungen): `security_level.csv`
nennt zwei Werte, `normal-SdT` und `erhöht` (773 und 227 im Katalog);
`effort_level.csv` sechs, 0 bis 5 (148 Anforderungen mit 0).
`sec_level`, `effort_level` und `tags` stehen an der Anforderung,
`documentation` an ihrem Statement.

Die Fassung des Konverters trägt die beiden Werte des BSI. Die des
Beispielordners trägt keinen davon (`normal-sdt`, `erhoeht-sdt`) und
lässt mit `effort` 1 bis 5 die 148 Anforderungen mit 0 nicht zu. Die
aktuelle ist also die des Konverters.

Nebenbefund: Das BSI hat sein Repository umgebaut und einen neueren
Katalog veröffentlicht als den, aus dem das Bundle konvertiert ist
(2026-07-16, 999 Anforderungen, festgehalten am Commit 39a1193). Eine
Anforderung ist dazugekommen, und der `ns` jeder Eigenschaft lautet
jetzt `documentation/namespaces/` statt `Dokumentation/namespaces/`.
Nichts davon ist umgestellt; das ist eine Entscheidung des Autors.

### #89: nicht gebaut, dem Autor erklärt

Der Ledger prüft, dass jeder Quellwert eine Regel hat und dass die Regel,
noch einmal angewandt, den Wert ergibt, der im Bundle steht. Er prüft
nicht, ob die Regel richtig ist, und nicht, ob der Wert an dem Ort
steht, den die Pfadkarte des Konverters nennt. Drei Konverter prüfen das
Zweite selbst. #89 wäre, diese Prüfung in die Bibliothek zu legen, damit
alle sechs sie haben. Kein Bundle ändert sich dadurch.

### Was beim Bauen anders kam als vorgelegt

1. **#82, „über Label oder Alias“.** Vorgeschlagen war, dass `#id` ein
   Objekt über sein Label oder einen Alias benennt. Gemessen trägt das
   Label nur 232 der 348 Verweise auf Controls (`#ac-11.1` gegen das
   Label `AC-11(1)`). Was alle 348 trägt, ist das Ende der Objekt-id
   nach dem letzten `/`, mit A bis Z wie a bis z. So ist es gebaut. Über
   einen Alias verweist kein Text der fünf Bundles; das ist nicht gebaut.
2. **#82, eine fünfte Art.** Im IFA-Bundle nennt ein Link die uuid
   seines Quelldokuments. Sie steht in `provenance.sources` des
   Manifests. Ohne diese Art hätte der Bericht einen auflösbaren Verweis
   als „ins Leere“ gezählt.
3. **#82, Statement-Form.** `#ac-2_smt.a` ist Objekt, Unterstrich,
   Statement-id. Das ist die Form der Quelle (NIST), nicht eine des
   Kernels; D9 schreibt sie als das fest, was ein Validator auflöst.
4. **#93, welche Kanten.** Der Autor hat „Regel bauen“ gesagt, nicht,
   welche Verweise sie trifft. Festgelegt von mir, aus den Messungen und
   aus früheren Entscheidungen:
   - Gehalten werden zwölf benannte Kanten an Tailoring, Mapping,
     Component, Implementation, Check und lebendem Risk.
   - Nicht gehalten: `replaces`, `canonical-alias`, `relations` (sie
     führen das Protokoll; 337 Fälle in CSF und SP 800-53); die
     Mitglieder eines Sets (Entscheidung E1: Ein Katalog listet, was er
     zurückgezogen hat; 220 Fälle).
   - Nicht gehalten: Assessment, Finding und Attestation. Sie halten
     fest, was zu einem Zeitpunkt gefunden oder unterschrieben wurde, und
     bleiben wahr. Ein Assessment über mehrere Subjekte lässt sich nicht
     für eines davon zurückziehen.
   - Die `treatments` eines Risk bleiben bei RISK-11, das diesen Fall
     schon als Fehler führt; sonst gäbe es zwei Fehler für einen Mangel.
   - Ein Objekt im Zustand `draft` oder `deprecated`, das sich stützt,
     wird gehalten wie ein aktives; ein Ziel im Zustand `deprecated` ist
     kein Fehler.
   Das ist in jedem Validator eine Tabelle und lässt sich ändern.
5. **Reader.** WITHDRAWN-1 steht auch im Reader (1.19.0), weil er
   Bundles schreibt. FRAGMENT-1 steht dort nicht: Der Reader führt keinen
   der Berichte.
6. **Validate-Seite der App.** Der Block „Autoren“ zeigte seit 0.9.17
   auch DRAFT-1-Zeilen und zählte sie als Autorenzeilen. Seit 0.9.20
   stehen dort nur AUTHOR-Zeilen; DRAFT-1 und FRAGMENT-1 stehen als
   Hinweise ihres Bereichs in der Liste darunter.

## Fünf Antworten des Autors, letzte Runde des Tages (2026-11-14)

Vorgelegt waren fünf Fragen. Die Antwort des Autors, wörtlich:

> 1 ja, 2 ja, 3 ja, 4 jetzt, 5 ja

1. **WITHDRAWN-1: die Kanten bleiben, wie gebaut.** Nichts zu ändern.
2. **#94 wie vorgeschlagen.** Der Beispielordner übernimmt Schema und
   Payload-Form des Konverters; seine Attestation ist neu ausgestellt. Der
   Konverter bricht bei einer Stufe ab, die die Liste des BSI nicht führt.
3. **Das Taxonomie-Schema ist echt typisiert**, Version 1.1.0: je
   Statement `class`, `sec-level` (`normal-SdT`, `erhöht`), `effort` (0
   bis 5), `tags`, sonst nichts.
4. **Grundschutz++ steht auf dem Katalog des BSI vom 2026-10-29**:
   1.000 Anforderungen, 289 Sets. Die Quelle ist am Commit `10f3c22` des
   BSI festgehalten.
5. **#89 ist gebaut**: Die Bibliothek prüft, ob jeder Wert dort steht, wo
   die Pfadkarte es sagt. Alle sechs Konverter mit Ledger nutzen sie.

### Was beim Bauen anders kam als vorgelegt

1. **Das BSI hat die Namensräume seiner Eigenschaften umbenannt**
   (`Dokumentation/namespaces/` zu `documentation/namespaces/`). Der
   Konverter in der alten Fassung lief auf dem neuen Katalog mit Exit 0,
   las keine einzige Eigenschaft und schrieb 1.000 Statements mit
   Modalität „unspecified“. Jeder Wert stand unverändert im compat-Facet,
   also meldete der Ledger nichts. Der Konverter liest jetzt den neuen
   Namensraum und bricht ab, wenn alle Eigenschaften eines Namens in
   einem fremden Namensraum stehen. Das App-Preset tut dasselbe.
2. **Version 1.1.0 statt 1.0.0.** Das Verzeichnis der gepinnten Schemas
   führt 1.0.0 als veröffentlicht; ein geändertes Schema bekommt eine
   neue Version. Die Zeile für 1.0.0 bleibt stehen.
3. **„Byte für Byte dieselbe Datei“ gilt nicht.** Die konvertierten
   Bundles liegen mit CRLF im Repository, der Beispielordner mit LF. Es
   sind zwei Dateien mit zwei Prüfsummen und ein Schema. Mein erster Push
   hatte die Prüfsumme der CRLF-Fassung gepinnt und war in allen vier
   CI-Jobs rot; lokal war er grün, weil die Arbeitskopie noch CRLF hatte.
4. **Die Prüfung „eine id und Version, ein Schema“ liest jetzt auch den
   Beispielordner.** Auf dem alten Stand schlägt sie an und nennt dessen
   Datei. Vorher sah sie dort nicht hin, deshalb gab es #94.
5. **#89, woher die Einträge kommen.** Je Zeile der Pfadkarte stehen die
   Orte, die der Ledger der festgehaltenen Quelle gemessen hat. Für ISM
   und CSF habe ich jeden Eintrag gegen den Satz der Zeile gelesen; vier
   Sätze nannten einen Ort nicht und nennen ihn jetzt. Für SP 800-53,
   CR26 und IFA sind es die gemessenen Orte, nicht Satz für Satz
   gegengelesen. Einige Orte stammen aus dem Code, weil nur erfundene
   Testkataloge sie erreichen.
6. **#89, was es nicht fängt.** Eine Regel, die den falschen Wert an den
   richtigen Ort schreibt, besteht auch diese Prüfung. Der Fall aus
   Punkt 1 ebenso: Die Eigenschaften standen an einem Ort, den die Zeile
   nennt. Dafür gibt es jetzt die eigene Sperre im Konverter.
7. **Zwei Nebenbefunde, nicht geändert (#95):** Der CR26-Konverter
   meldet Widersprüche zwischen Pfadkarte und Ledger, bricht aber nicht
   daran ab. Die IFA-Pfadkarte hat eine Zeile, die kein Pfad erreicht.

## #95 (2026-11-15)

Dem Autor erklärt, mit einem Vorschlag je Teil. Die Antwort, wörtlich:

> Beides

1. **CR26:** Ein Widerspruch zwischen Pfadkarte und Ledger beendet den
   Lauf mit 1. Vorher wurde er gedruckt und berichtet, und der Lauf
   endete mit 0, wenn keine andere Sperre griff.
2. **IFA:** Die Zeile der Pfadkarte, die kein Pfad erreicht, ist
   gestrichen, mit ihrem Eintrag in der Ortstabelle.

Kein Bundle, kein Bericht und kein Ledger hat sich geändert.
