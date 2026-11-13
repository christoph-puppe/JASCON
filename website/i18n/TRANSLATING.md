# Translating jascon.net

The site is written in English (`website/src/`). German, Hindi, Japanese and
Simplified Chinese are built from translations of it:

| Language | Folder of the pages | Strings of the layout | Served at |
|---|---|---|---|
| Deutsch | `src/de/` | `i18n/de.json` | `/de/` |
| हिन्दी (Hindi) | `src/hi/` | `i18n/hi.json` | `/hi/` |
| 日本語 | `src/ja/` | `i18n/ja.json` | `/ja/` |
| 简体中文 | `src/zh/` | `i18n/zh.json` | `/zh/` |

A language is built when `site.json` lists it under `"languages"`. A page
that has no translation is not built in that language; its links go to the
English page.

## The workflow

1. Translate `src/<page>.html` into `src/<lang>/<page>.html`, and
   `src/_check-demo.html` into `src/<lang>/_check-demo.html`.
2. Check the structure:
   `python3 website/i18n/check_translation.py <lang> <page>`.
3. Record that the translation follows the English page as it stands:
   `python3 website/build.py --stamp <lang>/<page>`. This writes the line
   `source: <digest>` into the header.
4. Build. When an English page changes later, its digest changes, the build
   lists the translation as older, and the translated page shows a note with
   a link to the English page until steps 1 to 3 are done again.

## What changes and what stays

A translation changes words, not the page.

- **Header.** Translate the values of `title` and `description`; copy the
  other lines (`nav`, `class`, `robots`). Each value stays on one line.
- **Markup.** Every element, `id`, `class`, `href`, `src`, `data-*`
  attribute and `{{ name }}` stays as it is, in the same blocks.
  Inside a paragraph or a table cell the order of inline elements (`<a>`,
  `<b>`, `<code>`, `<em>`) may change with the word order. Translate the
  attributes a reader sees: `title`, `aria-label`, `alt`, `placeholder`.
- **Code.** `<pre>`, `<code>`, `<kbd>`, `<script>` and `<textarea>` stay
  English, inline code too. In a `<code data-lang="sh">` block the comment
  lines (starting with `#`) may be translated.
- **Diagram labels.** The short `<text>` labels of the SVG diagrams are
  translated, the object type names in them are not. Keep a label as short
  as the English one; the boxes are 160 px wide.
- **Names.** JASCON, OSCAL, Gemara, CycloneDX, CISO Assistant, SCAP, XCCDF,
  NIST, BSI, ASD, ISO/IEC 27001, file names, field names, commands and
  version numbers stay as written.
- **Object types.** Where the English text names a JASCON type with a capital
  letter (Requirement, RequirementSet, Tailoring, Mapping, Risk, Component,
  Implementation, Assessment, Finding, Attestation, Check, Set), the type
  name stays English; the plain word ("a requirement", "the risk") is
  translated.
- **Verdicts.** Full Match, Semantic Match and Tamper are the names the
  specification defines; they stay English. The explanation is translated.
- **Numbers and dates.** `{{ n.* }}` and `{{ facts.* }}` are filled by the
  build with the language's separator. Numbers typed in the text follow the
  language: German `5.886`, the others `5,886`. Dates: `13. November 2026`,
  `13 नवंबर 2026`, `2026年11月13日`.
- **Tone.** The English text is measured: a claim says whether it was
  measured, is designed for, or is proposed, and states its limits. Keep
  that. Add nothing, leave nothing out, no marketing words. German uses
  "Sie"; Japanese uses です・ます in prose and plain forms in tables; Hindi
  uses आप.

## Glossary

| English | Deutsch | हिन्दी | 日本語 | 简体中文 |
|---|---|---|---|---|
| compliance data | Compliance-Daten | अनुपालन डेटा | コンプライアンスデータ | 合规数据 |
| standard, catalogue | Standard, Katalog | मानक, कैटलॉग | 標準、カタログ | 标准、目录 |
| control | Control | नियंत्रण | 管理策 | 控制措施 |
| tailoring | Tailoring | टेलरिंग | テーラリング | 裁剪 |
| risk | Risiko | जोखिम | リスク | 风险 |
| implementation | Umsetzung | कार्यान्वयन | 実装 | 实施 |
| assessment | Prüfung | मूल्यांकन | 評価 | 评估 |
| finding | Feststellung | निष्कर्ष | 指摘事項 | 发现项 |
| attestation | Attestierung | अनुप्रमाणन | 証明 | 证明 |
| evidence | Nachweis | साक्ष्य | 証跡 | 证据 |
| check (by a machine) | Check, maschinelle Prüfung | जाँच | チェック | 检查 |
| verdict | Urteil | निर्णय | 判定 | 判定 |
| observation | Beobachtung | अवलोकन | 観測値 | 观测值 |
| collector | Kollektor | संग्राहक (collector) | コレクター | 采集器 |
| Statement of Applicability | Erklärung zur Anwendbarkeit (SoA) | प्रयोज्यता विवरण (SoA) | 適用宣言書 (SoA) | 适用性声明 (SoA) |
| package digest | Paket-Digest | पैकेज डाइजेस्ट | パッケージダイジェスト | 包摘要 |
| semantic digest | semantischer Digest | सिमेंटिक डाइजेस्ट | セマンティックダイジェスト | 语义摘要 |
| bundle | Bundle | बंडल | バンドル | 捆绑包 |
| facet | Facette | फ़ेसेट | ファセット | 分面（facet） |
| round trip | Round Trip | राउंड ट्रिप | ラウンドトリップ | 往返转换 |
| conformance vectors | Konformitätsvektoren | अनुरूपता वेक्टर | 適合性テストベクトル | 一致性测试向量 |
| validator | Validator | वैलिडेटर | バリデータ | 校验器 |
| prior art | Stand der Technik | पूर्ववर्ती कार्य | 先行技術 | 现有技术 |
| measured | gemessen | मापा गया | 実測 | 实测 |
| designed | entworfen | डिज़ाइन किया गया | 設計済み | 已设计 |
| proposed | vorgeschlagen | प्रस्तावित | 提案 | 提议 |
| 2.0.0 candidate | Kandidat für 2.0.0 | 2.0.0 हेतु प्रस्तावित | 2.0.0 候補 | 2.0.0 候选 |
| yes / no / partial / tool only | ja / nein / teilweise / nur im Tool | हाँ / नहीं / आंशिक / केवल टूल में | あり / なし / 一部 / ツールのみ | 是 / 否 / 部分 / 仅限工具 |
| the app | die App | ऐप | アプリ | 应用 |
| Get started | Erste Schritte | शुरुआत करें | はじめに | 快速开始 |
| Join | Mitmachen | जुड़ें | 参加する | 参与 |
| Evidence (the page) | Belege | प्रमाण | 根拠 | 依据 |
| The model (the page) | Das Modell | मॉडल | モデル | 模型 |
| this project | dieses Projekt | यह परियोजना | 本プロジェクト | 本项目 |
