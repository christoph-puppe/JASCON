"""I-Regexp (RFC 9485) recogniser plus a PCRE/RE2 feature scanner and mechanical rewriter.

Grammar: transcribed from iregexp.abnf in github.com/ietf-wg-jsonpath/iregexp (the
source of RFC 9485; rfc-editor.org was not reachable from this sandbox), including the
extra rule that `[^]` is not allowed.

classify(regex) returns a dict:
  tier "A_inside"        : after whole-value normalisation of edge anchors (leading ^ /
                           trailing $ removed, unanchored ends padded with .*), the
                           pattern is a valid I-Regexp with the same boolean meaning.
  tier "B_rewritable"    : only uses features with a mechanical, meaning-preserving
                           rewrite into I-Regexp (e.g. \\s -> [ \\t\\n\\r], \\d -> [0-9],
                           (?: -> (, lazy -> greedy, needless escapes, POSIX classes,
                           leading (?i) -> case-fold expansion); the rewrite is verified
                           with the recogniser.
  tier "C_outside"       : uses at least one feature with no I-Regexp equivalent
                           (lookaround, backreference, \\b, interior/multiline anchors,
                           mid-pattern or non-i flags, possessive/atomic, ...).
  features               : every non-I-Regexp feature found (counted per regex).
"""

SINGLE_CHAR_ESC = set("()*+-.?[\\]^nrt{|}")
NOT_NORMAL = set("()*+.?[\\]{|}")
CAT = {"L": "lmotu", "M": "cen", "N": "dlo", "P": "cdefios", "Z": "lps", "S": "ckmo", "C": "cfno"}


class _P:
    def __init__(self, s):
        self.s, self.i = s, 0

    def peek(self, k=0):
        j = self.i + k
        return self.s[j] if j < len(self.s) else None

    def eat(self, c=None):
        ch = self.peek()
        if ch is None or (c is not None and ch != c):
            raise ValueError("expected %r at %d" % (c, self.i))
        self.i += 1
        return ch


def is_iregexp(s):
    p = _P(s)
    try:
        _regexp(p)
        if p.i != len(s):
            return False
        return True
    except ValueError:
        return False


def _regexp(p):
    _branch(p)
    while p.peek() == "|":
        p.eat()
        _branch(p)


def _branch(p):
    while p.peek() is not None and p.peek() not in "|)":
        _piece(p)


def _piece(p):
    _atom(p)
    c = p.peek()
    if c in ("*", "+", "?"):
        p.eat()
    elif c == "{":
        p.eat()
        n = 0
        while p.peek() is not None and p.peek().isdigit() and p.peek() in "0123456789":
            p.eat()
            n += 1
        if n == 0:
            raise ValueError("quant")
        if p.peek() == ",":
            p.eat()
            while p.peek() is not None and p.peek() in "0123456789":
                p.eat()
        p.eat("}")


def _atom(p):
    c = p.peek()
    if c is None:
        raise ValueError("eof")
    if c == "(":
        p.eat()
        _regexp(p)
        p.eat(")")
    elif c == ".":
        p.eat()
    elif c == "\\":
        _escape(p, in_class=False)
    elif c == "[":
        _class(p)
    elif c in NOT_NORMAL:
        raise ValueError("not normal char %r" % c)
    else:
        p.eat()


def _escape(p, in_class):
    p.eat("\\")
    c = p.peek()
    if c is None:
        raise ValueError("eof esc")
    if c in SINGLE_CHAR_ESC:
        p.eat()
        return "single"
    if c in ("p", "P"):
        p.eat()
        p.eat("{")
        major = p.eat()
        if major not in CAT:
            raise ValueError("cat")
        if p.peek() != "}":
            minor = p.eat()
            if minor not in CAT[major]:
                raise ValueError("cat minor")
        p.eat("}")
        return "cat"
    raise ValueError("bad escape \\%s" % c)


def _ccchar(p):
    c = p.peek()
    if c is None:
        raise ValueError("eof cc")
    if c == "\\":
        if p.peek(1) in ("p", "P"):
            raise ValueError("not ccchar")
        _escape(p, True)
        return
    if c in "-[]":
        raise ValueError("ccchar")
    p.eat()


def _is_ccchar_start(p, k=0):
    c = p.peek(k)
    if c is None:
        return False
    if c == "\\":
        n = p.peek(k + 1)
        return n is not None and n in SINGLE_CHAR_ESC
    return c not in "-[]"


def _cce1(p):
    if p.peek() == "\\" and p.peek(1) in ("p", "P"):
        _escape(p, True)
        return
    _ccchar(p)
    if p.peek() == "-" and _is_ccchar_start(p, 1):
        p.eat("-")
        _ccchar(p)


def _class(p):
    p.eat("[")
    if p.peek() == "^":
        if p.peek(1) == "]":
            raise ValueError("[^] not allowed")
        p.eat()
    if p.peek() == "-":
        p.eat()
    else:
        _cce1(p)
    while p.peek() is not None and p.peek() not in "]" and not (p.peek() == "-" and p.peek(1) == "]"):
        _cce1(p)
    if p.peek() == "-":
        p.eat()
    p.eat("]")


# ---------------------------------------------------------------- PCRE scanning/rewrite

POSIX = {
    "alpha": "A-Za-z", "digit": "0-9", "alnum": "A-Za-z0-9", "upper": "A-Z", "lower": "a-z",
    "space": " \\t\\n\\r\x0b\x0c", "blank": " \\t", "xdigit": "0-9A-Fa-f",
    "print": " -~", "graph": "!-~", "punct": "!-/:-@\\[-`\\{-~", "cntrl": "\x00-\x1f\x7f",
    "word": "A-Za-z0-9_",
}
MCE_OUT = {"s": "[ \\t\\n\\r]", "S": "[^ \\t\\n\\r]", "d": "[0-9]", "D": "[^0-9]",
           "w": "[A-Za-z0-9_]", "W": "[^A-Za-z0-9_]", "h": "[ \\t]", "H": "[^ \\t]"}
MCE_IN = {"s": " \\t\\n\\r", "d": "0-9", "w": "A-Za-z0-9_", "h": " \\t"}


ANCHOR_S, ANCHOR_E = "", ""  # sentinels for edge anchors in rewritten text


def _lit(ch, in_class):
    """I-Regexp spelling of a literal character."""
    if ch == "\n":
        return "\\n"
    if ch == "\r":
        return "\\r"
    if ch == "\t":
        return "\\t"
    if in_class:
        return "\\" + ch if ch in "-[]\\^" else ch
    return "\\" + ch if ch in NOT_NORMAL else ch


def _fold(ch):
    if ch.isalpha() and ch.lower() != ch.upper():
        return "[%s%s]" % (ch.lower(), ch.upper())
    return None


CTRL = {"f": "\x0c", "v": "\x0b", "e": "\x1b", "a": "\x07", "0": "\x00"}


def _close_class(tokens, negated, icase, feats):
    """tokens: list of ('c', literal_char) | ('raw', iregexp_text) | ('-',)."""
    items = []
    k = 0
    while k < len(tokens):
        t = tokens[k]
        if t[0] == "c" and k + 2 < len(tokens) and tokens[k + 1][0] == "-" and tokens[k + 2][0] == "c":
            items.append(("range", t[1], tokens[k + 2][1]))
            k += 3
            continue
        if t[0] == "-":
            items.append(("c", "-"))
        else:
            items.append(t)
        k += 1
    out = []
    for it in items:
        if it[0] == "range":
            a, b = it[1], it[2]
            out.append(_lit(a, True) + "-" + _lit(b, True))
            if icase and a.isalpha() and b.isalpha() and a.lower() != a.upper():
                feats.append("case_fold_needed")
                sa, sb = a.swapcase(), b.swapcase()
                out.append(_lit(sa, True) + "-" + _lit(sb, True))
        elif it[0] == "c":
            out.append(_lit(it[1], True))
            if icase and it[1].isalpha() and it[1].lower() != it[1].upper():
                feats.append("case_fold_needed")
                out.append(it[1].swapcase())
        else:
            out.append(it[1])
    return "[" + ("^" if negated else "") + "".join(out) + "]"


def scan(regex):
    """Walk PCRE/RE2 syntax. Return (rewritten I-Regexp candidate, features, blocking)."""
    import re as _re
    s, n = regex, len(regex)
    feats, blocking, out = [], set(), []
    i, depth, icase = 0, 0, False
    while i < n:
        c = s[i]
        if c == "[":
            neg = s.startswith("[^", i)
            i += 2 if neg else 1
            toks = []
            first = True
            while i < n and not (s[i] == "]" and not first):
                c2 = s[i]
                first = False
                if c2 == "[" and s.startswith("[:", i) and s.find(":]", i) > 0:
                    j = s.find(":]", i)
                    name = s[i + 2:j]
                    if name in POSIX:
                        feats.append("posix_class[:%s:]" % name)
                        toks.append(("raw", POSIX[name]))
                        i = j + 2
                        continue
                if c2 == "\\":
                    e = s[i + 1] if i + 1 < n else ""
                    if e in MCE_IN:
                        feats.append("mce_\\%s" % e)
                        toks.append(("raw", MCE_IN[e]))
                    elif e in ("S", "D", "W", "H"):
                        feats.append("mce_\\%s" % e)
                        # [\S] on its own (not negated) is just \S; anything else needs subtraction
                        if not neg and not toks and s[i + 2:i + 3] == "]":
                            toks.append(("raw_class", MCE_OUT[e]))
                        else:
                            feats.append("complement_mce_inside_class")
                            blocking.add("complement_mce_inside_class")
                    elif e in ("n", "r", "t"):
                        toks.append(("c", {"n": "\n", "r": "\r", "t": "\t"}[e]))
                    elif e in SINGLE_CHAR_ESC:
                        toks.append(("c", e))
                    elif e in ("p", "P"):
                        j = s.find("}", i)
                        feats.append("unicode_property")
                        toks.append(("raw", s[i:j + 1]))
                        i = j + 1
                        continue
                    elif e == "x":
                        feats.append("hex_escape")
                        try:
                            toks.append(("c", chr(int(s[i + 2:i + 4], 16))))
                        except ValueError:
                            blocking.add("bad_hex")
                        i += 4
                        continue
                    elif e in CTRL:
                        feats.append("control_escape_\\%s" % e)
                        toks.append(("c", CTRL[e]))
                    elif e and not e.isalnum():
                        feats.append("escape_not_in_iregexp_\\%s" % e)
                        toks.append(("c", e))
                    else:
                        feats.append("unknown_escape_\\%s" % e)
                        blocking.add("unknown_escape")
                    i += 2
                    continue
                if c2 == "[":
                    feats.append("unescaped_[_in_class")
                if c2 == "-":
                    prev_ok = bool(toks) and toks[-1][0] == "c" and not (len(toks) >= 2 and toks[-2][0] == "-")
                    nxt = s[i + 1] if i + 1 < n else ""
                    if prev_ok and nxt != "]":
                        toks.append(("-",))
                    else:
                        if toks and nxt != "]":
                            feats.append("literal_hyphen_mid_class")
                        toks.append(("c", "-"))
                    i += 1
                    continue
                toks.append(("c", c2))
                i += 1
            if i >= n:
                blocking.add("unterminated_class")
                break
            i += 1  # ]
            # a trailing '-' token that never got its range end
            toks = [t if not (t[0] == "-" and k == len(toks) - 1) else ("c", "-") for k, t in enumerate(toks)]
            if len(toks) == 1 and toks[0][0] == "raw_class":
                out.append(toks[0][1])
            else:
                out.append(_close_class(toks, neg, icase, feats))
            continue
        if c == "\\":
            e = s[i + 1] if i + 1 < n else ""
            if e in MCE_OUT:
                feats.append("mce_\\%s" % e)
                out.append(MCE_OUT[e])
            elif e in ("b", "B"):
                feats.append("word_boundary_\\%s" % e)
                blocking.add("word_boundary")
            elif e in ("A", "z", "Z", "G"):
                feats.append("string_anchor_\\%s" % e)
                if e == "A" and i == 0:
                    out.append(ANCHOR_S)
                elif e in ("z", "Z") and i + 2 == n:
                    out.append(ANCHOR_E)
                else:
                    blocking.add("string_anchor_interior")
            elif e.isdigit() and e != "0" or e == "k":
                feats.append("backreference")
                blocking.add("backreference")
            elif e == "K":
                feats.append("match_reset_\\K")
                blocking.add("match_reset")
            elif e in ("n", "r", "t"):
                out.append("\\" + e)
            elif e in SINGLE_CHAR_ESC:
                out.append("\\" + e)
            elif e in ("p", "P"):
                j = s.find("}", i)
                feats.append("unicode_property")
                out.append(s[i:j + 1])
                i = j + 1
                continue
            elif e == "x":
                feats.append("hex_escape")
                try:
                    out.append(_lit(chr(int(s[i + 2:i + 4], 16)), False))
                except ValueError:
                    blocking.add("bad_hex")
                i += 4
                continue
            elif e in CTRL:
                feats.append("control_escape_\\%s" % e)
                out.append(CTRL[e])
            elif e and not e.isalnum():
                feats.append("escape_not_in_iregexp_\\%s" % e)
                out.append(_lit(e, False))
            else:
                feats.append("unknown_escape_\\%s" % e)
                blocking.add("unknown_escape")
            i += 2
            continue
        if c == "(":
            if s.startswith("(?", i):
                rest = s[i + 2:]
                mflag = _re.match(r"([a-zA-Z]*)(?:-([a-zA-Z]*))?([:)])", rest)
                if rest.startswith(":"):
                    feats.append("non_capturing_group(?:")
                    out.append("(")
                    i += 3
                elif rest[:1] in ("=", "!"):
                    feats.append("lookahead")
                    blocking.add("lookaround")
                    out.append("(")
                    i += 3
                elif rest[:2] in ("<=", "<!"):
                    feats.append("lookbehind")
                    blocking.add("lookaround")
                    out.append("(")
                    i += 4
                elif rest.startswith("P<") or rest.startswith("<"):
                    feats.append("named_group")
                    out.append("(")
                    i = s.find(">", i) + 1
                elif rest.startswith(">"):
                    feats.append("atomic_group")
                    blocking.add("atomic_group")
                    out.append("(")
                    i += 3
                elif rest.startswith("#"):
                    feats.append("comment_group")
                    i = s.find(")", i) + 1
                    continue
                elif mflag:
                    on, off, term = mflag.group(1), mflag.group(2) or "", mflag.group(3)
                    allf = set(on) | set(off)
                    where = "leading" if (i == 0 or (i == 1 and s[0] == "^")) else "mid"
                    feats.append("inline_flag_%s(?%s%s)" % (where, on, "-" + off if off else ""))
                    if allf - {"i"}:
                        blocking.add("inline_flag_not_i(%s)" % "".join(sorted(allf - {"i"})))
                    if term == ")":
                        if depth > 0:
                            blocking.add("inline_flag_scoped_in_group")
                        if "i" in on:
                            icase = True
                        if "i" in off:
                            icase = False
                        i += 2 + mflag.end()
                        continue
                    # (?i:...) scoped group
                    blocking.add("inline_flag_scoped_group")
                    out.append("(")
                    i += 2 + mflag.end()
                else:
                    feats.append("unknown_group_syntax")
                    blocking.add("unknown_group_syntax")
                    out.append("(")
                    i += 2
            else:
                out.append("(")
                i += 1
            depth += 1
            continue
        if c == ")":
            depth -= 1
            out.append(")")
            i += 1
            continue
        if c in "*+?":
            out.append(c)
            i += 1
            if i < n and s[i] == "?":
                feats.append("lazy_quantifier")
                i += 1
            elif i < n and s[i] == "+":
                feats.append("possessive_quantifier")
                blocking.add("possessive_quantifier")
                i += 1
            continue
        if c == "{":
            mq = _re.match(r"\{(\d+)(,(\d*))?\}", s[i:])
            if mq:
                out.append(mq.group(0))
                i += mq.end()
                if i < n and s[i] == "?":
                    feats.append("lazy_quantifier")
                    i += 1
                elif i < n and s[i] == "+":
                    feats.append("possessive_quantifier")
                    blocking.add("possessive_quantifier")
                    i += 1
                continue
            feats.append("literal_{_unescaped")
            out.append("\\{")
            i += 1
            continue
        if c in "]}":
            feats.append("literal_%s_unescaped" % c)
            out.append("\\" + c)
            i += 1
            continue
        if c == "^":
            prev = "".join(out)
            if depth == 0 and (prev == "" or prev.endswith("|") and not prev.endswith("\\|")):
                out.append(ANCHOR_S)
            else:
                feats.append("interior_anchor_^")
                blocking.add("interior_anchor")
            i += 1
            continue
        if c == "$":
            if depth == 0 and (i == n - 1 or s[i + 1] == "|"):
                out.append(ANCHOR_E)
            else:
                feats.append("interior_anchor_$")
                blocking.add("interior_anchor")
            i += 1
            continue
        if icase and _fold(c):
            feats.append("case_fold_needed")
            out.append(_fold(c))
        else:
            out.append(c)
        i += 1
    return "".join(out), feats, blocking


def _split_top(s):
    parts, depth, cur, i = [], 0, [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            cur.append(s[i:i + 2])
            i += 2
            continue
        if c == "[":
            j = i + 1
            if j < len(s) and s[j] == "^":
                j += 1
            j += 1
            while j < len(s) and s[j] != "]":
                j += 2 if s[j] == "\\" else 1
            cur.append(s[i:j + 1])
            i = j + 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "|" and depth == 0:
            parts.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur))
    return parts


def whole_value(rewritten):
    """Search-semantics pattern with sentinel edge anchors -> whole-value I-Regexp text."""
    res = []
    for b in _split_top(rewritten):
        pre, post = ".*", ".*"
        if b.startswith(ANCHOR_S):
            b, pre = b[1:], ""
        if b.endswith(ANCHOR_E):
            b, post = b[:-1], ""
        res.append(pre + b + post)
    return "|".join(res)


def classify(regex):
    rewritten, feats, blocking = scan(regex)
    raw_valid = is_iregexp(regex)
    wv = None
    if blocking:
        tier = "C_outside"
    else:
        wv = whole_value(rewritten)
        if ANCHOR_S in wv or ANCHOR_E in wv or not is_iregexp(wv):
            tier = "C_outside"
            blocking = set(blocking) | {"rewrite_failed_grammar"}
        elif not feats:
            tier = "A_inside"
        else:
            tier = "B_rewritable"
    return {"tier": tier, "raw_string_is_valid_iregexp_syntax": raw_valid, "features": feats,
            "blocking": sorted(blocking), "whole_value_iregexp": wv}
