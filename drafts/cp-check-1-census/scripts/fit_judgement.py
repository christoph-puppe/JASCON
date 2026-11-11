"""JUDGEMENT (not mechanical): fit class of each selected CaC rule under the proposed comparator set.

Classes
  fits                 AND of {fact op literal|parameter} with ops in the proposed set, after the
                       collector normalises a value (effective value across config files/drop-ins/
                       built-in defaults, parse to int/bool/list/flag-set, enumerate resources), and
                       with an applicability guard moved to applies-when.
  needs-OR             two or more alternative compliant configurations over *different* facts that
                       are not an applicability guard and not just alternative config sources.
  needs-arithmetic     computation over values: counts/uniqueness, time vs now, bitwise mask against a
                       parameter, numeric fact-vs-fact range comparison.
  needs-regex-outside  comparison-side regex outside I-Regexp that cannot move to the collector.
  other:<why>          anything else (named).
Caveats are recorded where the "fits" verdict depends on a model decision.
"""

TEMPLATE = {
    # template: (class, one-line reasoning)
    "file_permissions": ("fits", "mode bits as flag set: subset-of allowed bits (literal filemode); OVAL is per-bit booleans ANDed"),
    "file_groupowner": ("fits", "gid equals literal (one-of when a list is given); files enumerated by collector"),
    "file_owner": ("fits", "uid equals literal (one-of when a list); files enumerated by collector"),
    "package_removed": ("fits", "package-installed boolean equals false / absent"),
    "sysctl": ("fits", "runtime and persisted value equals/one-of (literal or parameter); OVAL ORs over sysctl.d files = collector normalisation"),
    "service_disabled": ("fits", "unit enabled/active booleans equal false; 'package not installed' OR branch -> applies-when"),
    "mount_option": ("fits", "mount options list includes-all [opt]; 'mount need not exist' -> applies-when mount present"),
    "audit_rules_dac_modification": ("fits", "collector normalises loaded rules (augenrules|auditctl, b32/b64, syscall grouping) into canonical rule set; includes-all"),
    "audit_rules_watch": ("fits", "watch rule in canonical rule set: includes-all; source OR = normalisation"),
    "audit_rules_kernel_module_loading": ("fits", "as audit_rules_dac_modification"),
    "audit_rules_unsuccessful_file_modification": ("fits", "as audit_rules_dac_modification"),
    "audit_rules_privileged_commands": ("fits", "as audit_rules_watch"),
    "audit_rules_file_deletion_events": ("fits", "as audit_rules_dac_modification"),
    "kernel_module_disabled": ("fits", "two facts: install-command equals /bin/false|/bin/true (one-of) AND blacklisted equals true"),
    "package_installed": ("fits", "package-installed boolean equals true (EVR-pinned rules are split out as other)"),
    "accounts_password": ("fits", "pwquality value equals/at-least/at-most parameter (operation given in template)"),
    "sshd_lineinfile": ("fits", "effective sshd value (incl. built-in default; 'absent OR value' when is_default_value) equals literal/parameter"),
    "mount": ("fits", "mount point is a separate partition: present"),
    "package_installed_guard_var": ("fits", "installed equals true, applies-when parameter == value (caveat: applies-when must accept a parameter)"),
    "service_enabled": ("fits", "enabled/active equal true; package-installed guard -> applies-when"),
    "systemd_dropin_configuration": ("fits", "effective value across main file + drop-ins equals literal"),
    "service_enabled_guard_var": ("fits", "as package_installed_guard_var"),
    "pam_account_password_faillock": ("fits", "effective faillock value (faillock.conf or pam line) at-most/at-least parameter bounds"),
    "cis_banner": ("fits", "banner content present AND matches-not (\\\\v|\\\\r|\\\\m|\\\\s|OS name); needs (.|\\n|\\r)* since I-Regexp '.' excludes newlines"),
    "file_existence": ("fits", "exists boolean + owner/mode equals literal"),
    "service_disabled_guard_var": ("fits", "as package_installed_guard_var"),
    "grub2_bootloader_argument": ("fits", "kernel cmdline arg equals literal / at-least parameter; grub.cfg|grubenv|default OR = normalisation"),
    "sudo_defaults_option": ("fits", "Defaults option present / equals parameter"),
    "package_removed_guard_var": ("fits", "as package_installed_guard_var"),
    "socket_disabled": ("fits", "socket unit enabled/active equal false"),
    "pam_options": ("fits", "pam_wheel line present with args: equals parameter / includes-all [use_uid]"),
}

# rule-level overrides for template rules (judgement)
TEMPLATE_RULE_OVERRIDE = {
    "package_pam_modules_installed": ("other:version-ordering", "evr@ubuntu2404 0:1.5.3-5 needs dpkg EVR ordering; no version type/op in proposed set"),
    "package_pam_runtime_installed": ("other:version-ordering", "evr@ubuntu2404 0:1.5.3-5 needs dpkg EVR ordering; no version type/op in proposed set"),
}

STATIC = {
    "account_unique_id": ("needs-arithmetic", "count(uids) == count(unique uids)"),
    "account_unique_name": ("needs-arithmetic", "count == count(unique)"),
    "group_unique_id": ("needs-arithmetic", "count == count(unique)"),
    "group_unique_name": ("needs-arithmetic", "count == count(unique)"),
    "accounts_password_last_change_is_in_past": ("needs-arithmetic", "last change date <= now (time_difference)"),
    "accounts_umask_etc_bashrc": ("needs-arithmetic", "bitwise AND of umask with parameter var_accounts_user_umask"),
    "accounts_umask_etc_login_defs": ("needs-arithmetic", "bitwise AND with parameter"),
    "accounts_umask_etc_profile": ("needs-arithmetic", "bitwise AND with parameter"),
    "all_apparmor_profiles_in_enforce_complain_mode": ("needs-arithmetic", "count(enforce)+count(complain) == count(loaded)"),
    "firewall_single_service_active": ("needs-arithmetic", "exactly one active firewall service (count == 1); no cardinality op"),
    "ntp_single_service_active": ("needs-arithmetic", "exactly one active time service (count == 1)"),
    "no_shelllogin_for_systemaccounts": ("needs-arithmetic", "uid < UID_MIN / SYS_UID_MAX read from login.defs (fact-vs-fact range), with OR on which keys are defined"),
    "chronyd_configure_pool_and_server": ("needs-OR", "server lines OR pool lines configured (two facts, two parameters)"),
    "sshd_limit_user_access": ("needs-OR", "AllowUsers OR AllowGroups OR DenyUsers OR DenyGroups set"),
    "directory_permissions_var_log_audit": ("needs-OR", "expected mode depends on another fact (log_group root vs not)"),
    "file_permissions_var_log_audit": ("needs-OR", "expected mode depends on log_group; nested OR/negate depth 4"),
    "file_group_ownership_var_log_audit": ("needs-OR", "XOR: logs root-group-owned XOR log_group != root"),
    "no_invalid_shell_accounts_unlocked": ("needs-OR", "per-account implication (invalid shell -> locked); fits only if applies-when can filter per resource"),
    "accounts_user_dot_group_ownership": ("other:cross-fact", "dotfile gid must equal its user's gid (join, expected is another fact)"),
    "accounts_user_dot_user_ownership": ("other:cross-fact", "dotfile uid must equal its user's uid"),
    "file_groupownership_home_directories": ("other:cross-fact", "home dir gid equals user's gid"),
    "file_ownership_home_directories": ("other:cross-fact", "home dir uid equals user's uid"),
    "gid_passwd_group_same": ("other:cross-fact", "every passwd gid exists in /etc/group (subset-of another fact)"),
}
STATIC_CAVEATS = {
    "auditd_data_retention_max_log_file_action": "OVAL 'case insensitive equals': collector must lower-case",
    "dconf_gnome_screensaver_idle_delay": "OVAL 'not equal 0' rewritten as at-least 1",
    "account_disable_post_pw_expiration": "OVAL 'greater than -1' rewritten as at-least 0",
    "file_ownerships_var_log": "expected owners depend on whether a syslog user exists; one-of {root,syslog} accepted",
    "accounts_no_uid_except_zero": "collector must emit names of uid-0 accounts (OVAL does it with a lookahead extraction regex)",
    "sshd_set_maxstartups": "collector splits 'a:b:c' into three integers",
    "sshd_use_strong_ciphers": "list fact subset-of allowed; OVAL encodes it as a regex",
    "postfix_network_listening_disabled": "'postfix disabled OR loopback-only' -> applies-when postfix enabled",
    "chronyd_run_as_chrony_user": "'user absent OR _chrony' -> effective value with default",
}

SCE = {
    "check_ufw_active": ("fits", "ufw active equals true"),
    "nftables_ensure_default_deny_policy": ("fits", "base chain policies equal drop"),
    "set_ip6tables_default_rule": ("fits", "chain policies one-of DROP|REJECT"),
    "set_iptables_default_rule": ("fits", "chain policies one-of DROP|REJECT"),
    "set_ufw_default_rule": ("fits", "default policies one-of deny|reject"),
    "set_ipv6_loopback_traffic": ("fits", "normalised rule set includes-all loopback rules"),
    "set_loopback_traffic": ("fits", "normalised rule set includes-all loopback rules"),
    "set_nftables_loopback_traffic": ("fits", "normalised rule set includes-all loopback rules"),
    "set_ufw_loopback_traffic": ("fits", "normalised rule set includes-all loopback rules"),
    "set_nftables_base_chain": ("fits", "base chains present"),
    "set_nftables_table": ("fits", "table present"),
    "file_permissions_unauthorized_world_writable": ("fits", "world-writable files list absent"),
    "file_permissions_ungroupowned": ("fits", "ungrouped files list absent"),
    "no_files_unowned_by_user": ("fits", "unowned files list absent"),
    "iptables_rules_for_open_ports": ("other:cross-fact", "every listening port has a rule (open ports subset-of rule ports)"),
    "ip6tables_rules_for_open_ports": ("other:cross-fact", "as iptables_rules_for_open_ports"),
    "ufw_rules_for_open_ports": ("other:cross-fact", "as iptables_rules_for_open_ports"),
    "audit_rules_privileged_commands": ("other:cross-fact", "every setuid/setgid binary found on disk has an audit rule"),
}


def judge(rule_id, rec):
    mech = rec["mechanism"]
    if mech == "template":
        if rule_id in TEMPLATE_RULE_OVERRIDE:
            c, why = TEMPLATE_RULE_OVERRIDE[rule_id]
            return c, why, None
        c, why = TEMPLATE.get(rec["template_name"], ("UNJUDGED", ""))
        return c, why, None
    if mech == "static_oval":
        if rule_id in STATIC:
            c, why = STATIC[rule_id]
            return c, why, None
        return "fits", "AND of value comparisons after normalisation (see mechanical signals)", STATIC_CAVEATS.get(rule_id)
    if mech == "sce_only":
        c, why = SCE.get(rule_id, ("UNJUDGED", ""))
        return c, why, None
    return "UNJUDGED", "", None
