/* jascon.net - the page behaviour, one file, no dependencies.

   Everything here is an addition: with scripts off, every page still reads
   in full (tab panels are all shown, nothing is hidden behind an animation).
   Nothing is sent anywhere; the only things stored are the colour scheme and
   the style you pick, in this browser's localStorage. */
(function () {
  "use strict";
  var root = document.documentElement;
  var $ = function (sel, el) { return (el || document).querySelector(sel); };
  var $$ = function (sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); };

  /* ---- colour scheme: the system's until the button is pressed ---- */
  var themeBtn = $("#theme");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("jascon-site:theme", next); } catch (e) { /* private mode */ }
    });
  }

  /* ---- style: classic until one of the three in styles.css is picked ---- */
  var STYLES = ["ledger", "engraving", "still-life"];
  var stylePick = $("#style");
  if (stylePick) {
    stylePick.value = root.getAttribute("data-style") || "";
    stylePick.addEventListener("change", function () {
      var s = STYLES.indexOf(stylePick.value) >= 0 ? stylePick.value : "";
      if (s) root.setAttribute("data-style", s); else root.removeAttribute("data-style");
      try {
        if (s) localStorage.setItem("jascon-site:style", s); else localStorage.removeItem("jascon-site:style");
      } catch (e) { /* private mode */ }
    });
  }

  /* ---- menu on small screens ---- */
  var menu = $("#menu"), nav = $("#nav");
  if (menu && nav) {
    menu.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menu.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) { nav.classList.remove("open"); menu.setAttribute("aria-expanded", "false"); }
    });
  }

  /* ---- tabs: [data-tabs] holds [role=tab][data-panel=id] and the panels ---- */
  $$("[data-tabs]").forEach(function (group) {
    var tabs = $$("[role=tab]", group);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab, panel = document.getElementById(t.getAttribute("data-panel"));
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab); });
      tab.addEventListener("keydown", function (e) {
        var step = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (step) { e.preventDefault(); select(tabs[(i + step + tabs.length) % tabs.length], true); }
      });
    });
    var first = tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0] || tabs[0];
    if (first) select(first);
  });

  /* ---- copy buttons: [data-copy] copies the text of the element it names ---- */
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var src = document.getElementById(btn.getAttribute("data-copy"));
      if (!src || !navigator.clipboard) return;
      var text = $$(".line", src).length
        ? $$(".line", src).map(function (l) { return l.textContent; }).join("\n")
        : src.textContent;
      navigator.clipboard.writeText(text.trim()).then(function () {
        var old = btn.textContent;
        btn.textContent = "copied";
        setTimeout(function () { btn.textContent = old; }, 1400);
      });
    });
  });

  /* ---- sections fade in once, when they come into view ---- */
  var reveals = $$(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- the two digests, computed in the page ----

     package digest  = SHA-256 over the bytes as they stand in the editor
     semantic digest = SHA-256 over the canonical form of the object without
                       its top-level `annotations` (members sorted by UTF-16
                       code units, no whitespace) - canonical() and sdig() of
                       jascon/scripts/validate_core.py

     The verdicts are the three of an attestation check (handbook ch. 11):
     both equal = Full Match, semantic equal only = Semantic Match, semantic
     differs = the content that was approved is not the content in hand. */
  var demo = $("#digest-demo");
  if (demo) {
    var area = $("textarea", demo);
    var original = area.value;
    var expect = JSON.parse($("#digest-expected").textContent);
    var out = {
      pkg: $("[data-out=package]", demo), sem: $("[data-out=semantic]", demo),
      pkgState: $("[data-state=package]", demo), semState: $("[data-state=semantic]", demo),
      verdict: $(".verdict", demo), title: $(".verdict-v", demo), text: $(".verdict p", demo)
    };

    var canon = function (v) {
      if (Array.isArray(v)) return "[" + v.map(canon).join(",") + "]";
      if (v && typeof v === "object") {
        return "{" + Object.keys(v).sort().map(function (k) {
          return JSON.stringify(k) + ":" + canon(v[k]);
        }).join(",") + "}";
      }
      return JSON.stringify(v);
    };
    var sha256 = function (text) {
      return crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)).then(function (buf) {
        return "sha256:" + Array.prototype.map.call(new Uint8Array(buf), function (b) {
          return b.toString(16).padStart(2, "0");
        }).join("");
      });
    };
    var mark = function (el, same) {
      el.textContent = same ? "unchanged" : "changed";
      el.className = same ? "same" : "diff";
    };
    var show = function (kind, title, text) {
      out.verdict.setAttribute("data-v", kind);
      out.title.textContent = title;
      out.text.textContent = text;
    };

    var update = function () {
      if (!(window.crypto && crypto.subtle)) {
        show("invalid", "Not available here", "This browser offers no SHA-256 on this page. Open the site over https, or run validate_core.py.");
        return;
      }
      var text = area.value, obj;
      try { obj = JSON.parse(text); } catch (e) { obj = undefined; }
      // the file ends with one newline; the editor shows it without
      sha256(text.replace(/\n*$/, "") + "\n").then(function (pkg) {
        out.pkg.textContent = pkg;
        mark(out.pkgState, pkg === expect.package);
        if (obj === undefined || obj === null || typeof obj !== "object" || Array.isArray(obj)) {
          out.sem.textContent = "-";
          mark(out.semState, false);
          show("invalid", "Not an object", "The text is not a JSON object, so there is no canonical form to digest. A validator stops here.");
          return;
        }
        var body = {};
        Object.keys(obj).forEach(function (k) { if (k !== "annotations") body[k] = obj[k]; });
        return sha256(canon(body)).then(function (sem) {
          out.sem.textContent = sem;
          mark(out.semState, sem === expect.semantic);
          if (sem !== expect.semantic) {
            show("tamper", "Tamper", "The meaning changed. The semantic digest no longer equals the one the attestation names, so the attestation does not cover this object.");
          } else if (pkg !== expect.package) {
            show("semantic", "Semantic Match", "The bytes changed, the meaning did not. The attestation still covers the object; the verifier reports that the packaging was altered.");
          } else {
            show("full", "Full Match", "Bytes and meaning are the ones recorded in the example bundle's content manifest.");
          }
        });
      });
    };

    var edit = {
      reindent: function (o) { return JSON.stringify(o, null, 4); },
      annotate: function (o) {
        o.annotations = Object.assign({}, o.annotations, { tracker: "GRC-" + (1000 + Math.floor(Math.random() * 9000)) });
        return JSON.stringify(o, null, 2);
      },
      reorder: function (o) {
        var r = {};
        Object.keys(o).reverse().forEach(function (k) { r[k] = o[k]; });
        return JSON.stringify(r, null, 2);
      },
      weaken: function (o) {
        if (o.statements && o.statements[0]) o.statements[0].modality = "should";
        return JSON.stringify(o, null, 2);
      }
    };
    $$("[data-edit]", demo).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var name = btn.getAttribute("data-edit");
        if (name === "reset") { area.value = original; update(); return; }
        try { area.value = edit[name](JSON.parse(area.value)); } catch (e) { /* not JSON: leave the text */ }
        update();
      });
    });
    area.addEventListener("input", update);
    update();
  }

  /* ---- check-verdict, computed in the page ----

     The two Checks of the example bundle against an observation the visitor
     sets. The verdict is not re-implemented here: the page loads the app's
     kernel rules (app/jascon-schema.js, app/jascon-rules.js), the port of
     validate_core.py that runs against the check vectors, and calls
     jscCheckVerdict and jscCheckAggregate. The scripts are fetched when the
     demo comes near the viewport, so pages without a visit to it pay
     nothing. */
  var cd = $("#check-demo");
  if (cd) {
    var data = JSON.parse($("#check-demo-data").textContent);
    var paramName = Object.keys(data.bound)[0];
    var ciphers = [];
    data.runs.forEach(function (r) {
      (r.facts["sshd.ciphers"] || []).forEach(function (c) { if (ciphers.indexOf(c) < 0) ciphers.push(c); });
    });
    var st = { param: data.bound[paramName], tries: 0, on: {}, silent: false, engine: "waiting" };
    var el = {
      param: $("#cd-param", cd), tries: $("#cd-tries", cd), paramText: $("[data-cd=param-text]", cd),
      ciphers: $("[data-cd=ciphers]", cd), presets: $("[data-cd=presets]", cd), rows: $("[data-cd=rows]", cd),
      silent: $("[data-cd-silent]", cd), verdict: $(".verdict", cd), v: $(".verdict-v", cd), vp: $(".verdict p", cd)
    };
    var make = function (tag, cls, text) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (text !== undefined) n.textContent = text;
      return n;
    };

    ciphers.forEach(function (c) {
      var label = make("label", "cd-check"), box = make("input");
      box.type = "checkbox"; box.value = c;
      box.addEventListener("change", function () { st.on[c] = box.checked; st.silent = false; draw(); });
      label.appendChild(box); label.appendChild(make("span", "", c));
      el.ciphers.appendChild(label);
    });
    var load = function (run) {
      st.tries = run.facts["sshd.maxauthtries"];
      ciphers.forEach(function (c) { st.on[c] = run.facts["sshd.ciphers"].indexOf(c) >= 0; });
      st.silent = false;
    };
    data.runs.forEach(function (run) {
      var b = make("button", "demo-btn", run.label);
      b.type = "button";
      b.appendChild(make("small", "", "recorded: " + run.result));
      b.addEventListener("click", function () { st.param = data.bound[paramName]; load(run); draw(); });
      el.presets.appendChild(b);
    });
    el.silent.addEventListener("click", function () { st.silent = true; draw(); });
    var clamp = function (input) {
      var n = Math.round(Number(input.value));
      if (!isFinite(n)) n = 1;
      return Math.min(10, Math.max(1, n));
    };
    el.param.addEventListener("input", function () { st.param = clamp(el.param); draw(true); });
    el.tries.addEventListener("input", function () { st.tries = clamp(el.tries); st.silent = false; draw(true); });

    var words = { "satisfied": "Satisfied", "not-satisfied": "Not satisfied", "inconclusive": "Inconclusive", "not-applicable": "Not applicable" };
    var kind = { "satisfied": "full", "not-satisfied": "tamper", "inconclusive": "invalid", "not-applicable": "semantic" };
    var criterion = function (a) {
      var e = a.expected;
      if (e && typeof e === "object" && !Array.isArray(e)) e = "{param: " + e.param + "} = " + st.param;
      else if (e !== undefined) e = JSON.stringify(e);
      return a.fact + " " + a.op + (e === undefined ? "" : " " + e);
    };

    function draw(typing) {
      if (!typing) { el.param.value = st.param; el.tries.value = st.tries; }
      el.paramText.textContent = st.param;
      $$("input", el.ciphers).forEach(function (b) { b.checked = !!st.on[b.value]; b.disabled = false; });
      cd.classList.toggle("silent", st.silent);
      el.rows.textContent = "";
      var ready = typeof jscCheckVerdict === "function" && typeof jscCheckAggregate === "function";
      var params = {}; params[paramName] = st.param;
      var observation = st.silent ? null : { facts: {
        "sshd.maxauthtries": st.tries,
        "sshd.ciphers": ciphers.filter(function (c) { return st.on[c]; })
      } };
      var outcomes = [];
      data.checks.forEach(function (check) {
        var row = make("div", "cd-row");
        var head = make("div", "cd-row-h");
        head.appendChild(make("b", "", check.title.en));
        var res = ready ? jscCheckVerdict(check, observation, params) : null;
        var pill = make("span", "cd-pill", res ? res[0] : st.engine === "failed" ? "no engine" : "loading");
        if (res) { pill.setAttribute("data-o", res[0]); outcomes.push(res[0]); }
        head.appendChild(pill);
        row.appendChild(head);
        row.appendChild(make("code", "", check.criteria.map(criterion).join(" and ")));
        row.appendChild(make("small", "", res ? (res[1].length ? res[1].join("; ") : "every criterion holds on the observation")
          : "clause " + check["statement-ids"].join(", ")));
        el.rows.appendChild(row);
      });
      if (!ready) {
        el.verdict.setAttribute("data-v", "invalid");
        el.v.textContent = st.engine === "failed" ? "Engine not found" : "Loading the rules";
        el.vp.textContent = st.engine === "failed"
          ? "The verdict is computed by the app's rules, which this copy of the site does not include. Open the Checks page of the app instead."
          : "The page fetches the app's kernel rules once.";
        return;
      }
      var all = jscCheckAggregate(outcomes);
      el.verdict.setAttribute("data-v", kind[all]);
      el.v.textContent = words[all];
      el.vp.textContent = all === "satisfied" ? "Both checks hold. The Assessment records each observation, so a second party reaches this verdict without running anything."
        : all === "not-satisfied" ? "One definite failure decides the aggregate. The failing row names the clause, and a Finding against that clause can point back to the check."
        : "No observation, no verdict: a default is never substituted. The row is recorded as inconclusive and must carry a reason.";
    }

    var fetched = false;
    var fetchEngine = function () {
      if (fetched) return;
      fetched = true;
      var files = ["app/jascon-schema.js", "app/jascon-rules.js"];
      (function next(i) {
        if (i === files.length) { st.engine = "ready"; draw(); return; }
        var sc = document.createElement("script");
        sc.src = files[i];
        sc.onload = function () { next(i + 1); };
        sc.onerror = function () { st.engine = "failed"; draw(); };
        document.head.appendChild(sc);
      })(0);
    };
    load(data.runs[0]);
    draw();
    if ("IntersectionObserver" in window) {
      var near = new IntersectionObserver(function (entries) {
        if (entries.some(function (en) { return en.isIntersecting; })) { near.disconnect(); fetchEngine(); }
      }, { rootMargin: "600px 0px" });
      near.observe(cd);
    } else {
      fetchEngine();
    }
  }
})();
