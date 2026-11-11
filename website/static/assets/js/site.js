/* jascon.net - the page behaviour, one file, no dependencies.

   Everything here is an addition: with scripts off, every page still reads
   in full (tab panels are all shown, nothing is hidden behind an animation).
   Nothing is sent anywhere; the only thing stored is the colour scheme you
   pick, in this browser's localStorage. */
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
})();
