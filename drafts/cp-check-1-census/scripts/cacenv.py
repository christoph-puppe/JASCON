"""Minimal re-implementation of the ComplianceAsCode Jinja rendering context for one product.

Does not import or execute any code from the downloaded repository: constants are read
from ssg/constants.py with `ast.literal_eval`, and the CaC Jinja delimiters/filters are
re-implemented here. Macros from shared/macros/*.jinja are loaded as (sandboxed) templates.
"""
import ast
import glob
import site
import sys

# -I drops user site-packages; jinja2 lives there. Append (lowest priority) the trusted user site.
if site.getusersitepackages() not in sys.path:
    sys.path.append(site.getusersitepackages())

import hashlib
import os
import re
from shlex import quote as shell_quote

import jinja2
import yaml
from jinja2.sandbox import SandboxedEnvironment


class LenientUndefined(jinja2.Undefined):
    """Undefined that renders empty, iterates empty and can be called (unknown macros)."""

    def __call__(self, *a, **k):
        return ""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return LenientUndefined()

    def __getitem__(self, k):
        return LenientUndefined()

    def __str__(self):
        return ""

    def __iter__(self):
        return iter(())

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, jinja2.Undefined)

    def __hash__(self):
        return 0


class AbsLoader(jinja2.BaseLoader):
    def get_source(self, environment, template):
        if not os.path.exists(template):
            raise jinja2.TemplateNotFound(template)
        with open(template, encoding="utf-8") as f:
            src = f.read()
        mtime = os.path.getmtime(template)
        return src, template, lambda: mtime == os.path.getmtime(template)


def escape_regex(text):
    return re.sub(r"([#$&*+.?^`|~:()\[\]-])", r"\\\1", text)


def banner_regexify(banner_text):
    return (escape_regex(banner_text).replace("\n", "BFLMPSVZ")
            .replace(" ", "[\\s\\n]+").replace("BFLMPSVZ", "(?:[\\n]+|(?:\\\\n)+)"))


def read_constants(root):
    path = os.path.join(root, "ssg/constants.py")
    with open(path) as f:
        tree = ast.parse(f.read())
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                consts[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    return consts


IMPLIED = {
    "dconf_gdm_dir": "DEFAULT_DCONF_GDM_DIR", "aide_conf_path": "DEFAULT_AIDE_CONF_PATH",
    "aide_bin_path": "DEFAULT_AIDE_BIN_PATH", "audit_watches_style": "DEFAULT_AUDIT_WATCHES_STYLE",
    "rsyslog_cafile": "DEFAULT_RSYSLOG_CAFILE", "sshd_distributed_config": "DEFAULT_SSH_DISTRIBUTED_CONFIG",
    "sshd_runtime_check": "DEFAULT_SSH_RUNTIME_CHECK", "sshd_main_config_file": "DEFAULT_SSHD_MAIN_CONFIG_FILE",
    "sshd_config_dir": "DEFAULT_SSHD_CONFIG_DIR",
    "sshd_hardening_config_basename": "DEFAULT_SSHD_HARDENING_CONFIG_BASENAME",
    "sshd_sysconfig_file": "DEFAULT_SSHD_SYSCONFIG_FILE",
    "ssh_client_main_config_file": "DEFAULT_SSH_CLIENT_MAIN_CONFIG_FILE",
    "ssh_client_config_dir": "DEFAULT_SSH_CLIENT_CONFIG_DIR",
    "openssh_client_crypto_policy_config_file": "DEFAULT_OPENSSH_CLIENT_CRYPTO_POLICY_CONFIG_FILE",
    "openssh_server_crypto_policy_config_file": "DEFAULT_OPENSSH_SERVER_CRYPTO_POLICY_CONFIG_FILE",
    "chrony_conf_path": "DEFAULT_CHRONY_CONF_PATH", "chrony_d_path": "DEFAULT_CHRONY_D_PATH",
    "audisp_conf_path": "DEFAULT_AUDISP_CONF_PATH", "faillock_path": "DEFAULT_FAILLOCK_PATH",
    "sysctl_remediate_drop_in_file": "DEFAULT_SYSCTL_REMEDIATE_DROP_IN_FILE",
    "bootable_containers_supported": "DEFAULT_BOOTABLE_CONTAINERS_SUPPORTED",
    "xwindows_packages": "DEFAULT_XWINDOWS_PACKAGES",
}


class CacEnv:
    def __init__(self, root, product="ubuntu2404"):
        self.root = os.path.abspath(root)
        self.consts = read_constants(self.root)
        self.env = SandboxedEnvironment(
            block_start_string="{{%", block_end_string="%}}",
            variable_start_string="{{{", variable_end_string="}}}",
            comment_start_string="{{#", comment_end_string="#}}",
            loader=AbsLoader(), undefined=LenientUndefined)
        self.env.filters.update({
            "banner_anchor_wrap": lambda t: "^" + t + "$",
            "banner_regexify": banner_regexify,
            "escape_id": lambda t: re.sub(r"[^\w]+", "_", t).strip("_"),
            "escape_regex": escape_regex,
            "escape_yaml_key": lambda t: re.sub(r"([A-Z^])", "^\\1", t).lower(),
            "quote": shell_quote,
            "sha256": lambda t: hashlib.sha256(t.encode()).hexdigest(),
        })
        props = self._product_props(product)
        self.props = props
        self.env.globals.update(props)
        self.env.globals.update({
            "product_to_name": self.product_to_name,
            "product_to_platform": lambda p: self._platforms(p),
            "name_to_platform": lambda n: "<platform>%s</platform>" % n if isinstance(n, str)
            else "\n".join("<platform>%s</platform>" % x for x in n),
            "raise": lambda m: (_ for _ in ()).throw(RuntimeError(m)),
            "url_encode": lambda s: s,
            "expand_yaml_path": lambda path, field: "",
        })
        self.macro_errors = []
        for fn in sorted(glob.glob(os.path.join(self.root, "shared/macros/*.jinja"))):
            try:
                mod = self.env.get_template(fn).make_module(dict(self.env.globals))
                for name, sym in mod.__dict__.items():
                    if not name.startswith("_"):
                        self.env.globals[name] = sym
            except Exception as e:  # keep going; record
                self.macro_errors.append((fn, repr(e)[:200]))

    def product_to_name(self, prod):
        for name, p in self.consts.get("FULL_NAME_TO_PRODUCT_MAPPING", {}).items():
            if p == prod:
                return name
        return "multi_platform_" + prod

    def _platforms(self, prods):
        if isinstance(prods, str):
            return "<platform>%s</platform>" % self.product_to_name(prods)
        return "\n".join(self._platforms(p) for p in prods)

    def _product_props(self, product):
        with open(os.path.join(self.root, "products", product, "product.yml")) as f:
            props = yaml.safe_load(f)
        c = self.consts
        if "pkg_manager" in props:
            props.setdefault("pkg_system", c.get("PKG_MANAGER_TO_SYSTEM", {}).get(props["pkg_manager"]))
        props.setdefault("groups", {})
        for k, cn in IMPLIED.items():
            if k not in props and cn in c:
                props[k] = c[cn]
        if "sshd_config_base_dir" not in props:
            props["sshd_config_base_dir"] = os.path.dirname(props["sshd_main_config_file"])
        pkg = dict(c.get("XCCDF_PLATFORM_TO_PACKAGE", {}))
        pkg.update(props.get("platform_package_overrides", {}))
        props["platform_package_overrides"] = pkg
        props["product_dir"] = os.path.join(self.root, "products", product)
        props["prodtype"] = product
        # product_properties/*.yml (default + overrides), rendered in order
        for fn in sorted(glob.glob(os.path.join(self.root, "product_properties/*.yml"))):
            tmp_env = SandboxedEnvironment(
                block_start_string="{{%", block_end_string="%}}",
                variable_start_string="{{{", variable_end_string="}}}",
                comment_start_string="{{#", comment_end_string="#}}",
                loader=AbsLoader(), undefined=LenientUndefined)
            txt = tmp_env.get_template(fn).render(dict(props))
            d = yaml.safe_load(txt) or {}
            merged = dict(d.get("default", {}) or {})
            merged.update(d.get("overrides", {}) or {})
            for k, v in merged.items():
                props.setdefault(k, v)
        return props

    def render_file(self, path, extra=None):
        ctx = dict(extra or {})
        return self.env.get_template(os.path.abspath(path)).render(ctx)
