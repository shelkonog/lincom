import json
import os
import re


def clear_list(rez_comp):
    for rez_comp_i in rez_comp[1]:
       rez_comp[0][rez_comp_i] = []


def write_list(rez_comp, key_cfg_stand, rez, key_cfg):
    rez_comp[0][rez_comp[1][0]].append(key_cfg[0])
    rez_comp[0][rez_comp[1][1]].append(str(key_cfg[1]))
    rez_comp[0][rez_comp[1][2]].append(key_cfg_stand)
    rez_comp[0][rez_comp[1][3]].append(rez)


def get_logrotate(lst_cmd):
    file_logrotate = '/etc/logrotate.conf'
    period = ['daily', 'weekly', 'monthly']
    count_rotate_re = re.compile(r"rotate\s*\d")

    if not os.path.exists(file_logrotate):
        logrotate_real = None
    else:
        logrotate_real = []
        for cmd in lst_cmd:
            params = []
            ls = os.popen(cmd).readlines()
            log_conf_files = [line.strip() for line in ls]
            count_rot = ''
            params_str = ''
            if file_logrotate in cmd:
                params.append('logrotate')
                for i in log_conf_files:
                    if i in period and len(params) == 1:
                        if count_rot == '':
                            params.append(i)
                        else:
                            params.append(i)
                            params[-1] = params[-1] + ', ' + count_rot
                    elif count_rotate_re.search(i):
                        if len(params) == 2:
                            params[-1] = params[-1] + ', ' + i
                        else:
                            count_rot = i
                logrotate_real.append(params)
            else:
                for i, conf_value in enumerate(log_conf_files):
                    if '/var/log' in conf_value or '{' in conf_value:
                        conf_value = conf_value.split()
                        if len(conf_value) == 1:
                            if conf_value != ['{']:
                                logrotate_real.append(conf_value)
                            else:
                                continue
                        else:
                            for conf_value_i in conf_value:
                                if conf_value_i != '{':
                                    logrotate_real.append([conf_value_i])
                                else:
                                    continue
                    elif conf_value in period and params_str == '':
                        if count_rot == '':
                            params_str = conf_value
                        else:
                            params_str = conf_value + ', ' + count_rot
                    elif count_rotate_re.search(conf_value):
                        if params_str != '':
                            params_str = params_str + ', ' + conf_value
                        else:
                            count_rot = conf_value
                    elif '}' in conf_value:
                        for conf_value_i in logrotate_real:
                            if len(conf_value_i) == 1:
                                conf_value_i.append(params_str)
                        params_str, count_rot = '', ''
                        continue
    return logrotate_real


def get_audit_rul(lst_cmd):
    audit_rul, dupl_el = [], {}

    for cmd in lst_cmd:
        ls = os.popen(cmd).readlines()

        ls = [line.strip().split() for line in ls]

        audit_rul = [line[-1].split('=') for line in ls]

        for link in audit_rul:
            item = link[-1]
            if item in dupl_el:
                dupl_el[item] += 1
            else:
                dupl_el[item] = 1

        audit_rul = list(dupl_el.items())

    return audit_rul


def pars_conf_space(ls):
    line = [line.strip().split() for line in ls]
    return line


def pars_conf_equally(ls):
    line = [line.strip().split('=') for line in ls]
    return line


def pars_conf_pwd(lst_cmd):
    conf_pwd = []
    for cmd in lst_cmd:
        list_serv = os.popen(cmd).readlines()
        if 'login.defs' in cmd:
            list_serv = pars_conf_space(list_serv)

            conf_pwd += list_serv.copy()
        elif 'pwquality.conf' in cmd:
            list_serv = pars_conf_equally(list_serv)

            conf_pwd += list_serv.copy()
        elif 'password' in cmd:
            list_serv = ''.join(list_serv).strip().split()
            list_serv = [line.split('=') for line in list_serv]

            conf_pwd += list_serv.copy()

    return conf_pwd


def pars_conf_serv(lst_cmd, stand_conf):
    list_serv = []
    for serv in stand_conf["services_conf"]:
        ls = os.popen(lst_cmd[0] + serv + " 2>/dev/null").read()
        if ls == '':
            list_serv.append([serv, 'removed'])
        else:
            list_serv.append([serv,  ls.strip()])

    for serv in stand_conf["client_conf"]:
        if os.path.exists('/usr/bin/dpkg'):
            ls = os.popen(lst_cmd[1] + serv + " 2>/dev/null").read()
        else:
            ls = os.popen(lst_cmd[2] + serv + " 2>/dev/null").read()
        if ls == '':
            list_serv.append([serv, 'removed'])
        else:
            list_serv.append([serv, 'enabled'])

    return list_serv


def get_conf(lst_cmd, name_conf, stand_conf):
    list_conf = []
    if name_conf == 'logrotate_conf':
        list_conf = get_logrotate(lst_cmd)

    elif name_conf == 'auditrule_conf':
        list_conf = get_audit_rul(lst_cmd)

    elif name_conf == 'password_conf':
        list_conf = pars_conf_pwd(lst_cmd)

    elif name_conf == 'services_conf':
        list_conf = pars_conf_serv(lst_cmd, stand_conf)

    else:
        for cmd in lst_cmd:
            list_serv = os.popen(cmd).readlines()
            list_params = []

            if name_conf == 'sshd_conf':
                list_params = pars_conf_space(list_serv)
            elif name_conf == 'journald_conf':
                list_params = pars_conf_equally(list_serv)
            elif name_conf == 'rsyslog_conf':
                list_params = pars_conf_space(list_serv)

            elif name_conf == 'auditd_conf':
                list_params = pars_conf_equally(list_serv)
                for index, lst_audit in enumerate(list_params):
                    lst_audit = [value.strip() for value in lst_audit]
                    list_params[index] = lst_audit

            for key_cfg in list_params:
                if (len(key_cfg) == 2):
                    list_conf.append(key_cfg.copy())

    return list_conf


def get_comp_conf(stand_conf, key, value):
    name_conf = key

    clear_list(value)

    list_serv = get_conf(value[2], name_conf, stand_conf)

    for key_cfg in list_serv:
        if (len(key_cfg) == 2) and stand_conf is not None:
            if key_cfg[0] in stand_conf[name_conf]:
                stand_rez = stand_conf[name_conf][key_cfg[0]]
                if str(key_cfg[1]) != stand_rez:
                    write_list(value, stand_rez, 'no', key_cfg)
                else:
                    write_list(value, stand_rez, 'pass', key_cfg)

    for params, params_value in stand_conf[name_conf].items():
        if params not in value[0][value[1][0]]:
            key_cfg = []
            key_cfg.append(params)
            key_cfg.append('---')
            write_list(value, params_value, 'no', key_cfg)

    return value[0]


def rez_comp_conf(file):
    try:
        with open(file, "r") as fh:
            stand_conf = json.load(fh)
    except json.JSONDecodeError:
        stand_conf = None
        print("json.JSONDecodeError")

    sshd_conf = {
            'key_ssh': [],
            'value_ssh': [],
            'value_stand_ssh': [],
            'status_ssh': []
        }

    auditd_conf = {
            'key_audit': [],
            'value_audit': [],
            'value_stand_audit': [],
            'status_audit': []
    }

    journald_conf = {
            'key_journal': [],
            'value_journal': [],
            'value_stand_journal': [],
            'status_journal': []
    }

    rsyslog_conf = {
                'key_rsyslog': [],
                'value_rsyslog': [],
                'value_stand_rsyslog': [],
                'status_rsyslog': []
        }

    logrotate_conf = {
                'key_logrotate': [],
                'value_logrotate': [],
                'value_stand_logrotate': [],
                'status_logrotate': []
        }

    auditrule_conf = {
                'key_auditrule': [],
                'value_auditrule': [],
                'value_stand_auditrule': [],
                'status_auditrule': []
        }

    password_conf = {
                'key_password': [],
                'value_password': [],
                'value_stand_password': [],
                'status_password': []
        }

    services_conf = {
                'key_services': [],
                'value_services': [],
                'value_stand_services': [],
                'status_services': []
        }

    cmd_ssh = ['sshd -T']
    cmd_audit = ["cat /etc/audit/auditd.conf"]
    cmd_journal = ["cat /etc/systemd/journald.conf | grep -v '^$'"]
    cmd_syslog = [
        "cat /etc/rsyslog.conf | grep -v '^#\|^$\|^\$'",
        "cat /etc/rsyslog.d/* 2>/dev/null | grep -v '^#\|^$\|^\$'",
        "cat /etc/syslog-ng/syslog-ng.conf | awk '/^destin/ {gsub(/[\{,\},\;,\"]/, \"\", $0) ;print $2\" \"$3}'"
                  ]
    cmd_logrotate = [
        "cat /etc/logrotate.conf | grep -v '^#\|^$'",
        "cat /etc/logrotate.d/* | grep -v '^#\|^$'"
    ]
    cmd_auditrule = ["auditctl -l"]
    cmd_password = [
        "cat /etc/login.defs | grep -v '^#\|^$'",
        "cat /etc/security/pwquality.conf | grep -v '^#\|^$'",
        "cat /etc/pam.d/common-password | grep minlen"
    ]
    cmd_sudoers = ["cat /etc/sudoers | awk -F= '/logfile/ {gsub(/Defaults/, "",$1); gsub(/\s/, "",$1); print $1" "$2}'"]
    cmd_services = ["systemctl is-enabled ", "dpkg -l ", "rpm -qa "]

    service_conf = {
        'sshd_conf': [sshd_conf, ['key_ssh', 'value_ssh', 'value_stand_ssh', 'status_ssh'], cmd_ssh],
        'auditd_conf': [auditd_conf, ['key_audit', 'value_audit', 'value_stand_audit', 'status_audit'], cmd_audit],
        'journald_conf': [journald_conf, ['key_journal', 'value_journal', 'value_stand_journal', 'status_journal'], cmd_journal],
        'rsyslog_conf': [rsyslog_conf, ['key_rsyslog', 'value_rsyslog', 'value_stand_rsyslog', 'status_rsyslog'], cmd_syslog],
        'logrotate_conf': [logrotate_conf, ['key_logrotate', 'value_logrotate', 'value_stand_logrotate', 'status_logrotate'], cmd_logrotate],
        'auditrule_conf': [auditrule_conf, ['key_auditrule', 'value_auditrule', 'value_stand_auditrule', 'status_auditrule'], cmd_auditrule],
        'password_conf': [password_conf, ['key_password', 'value_password', 'value_stand_password', 'status_password'], cmd_password],
        'services_conf': [services_conf, ['key_services', 'value_services', 'value_stand_services', 'status_services'], cmd_services]
    }

    for key, value in service_conf.items():
        yield get_comp_conf(stand_conf, key, value)


def foo_split_list(alist, wanted_parts=4):
    length = len(alist)
    return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts] for i in range(wanted_parts)]


def open_soft_list(file):
    try:
        with open(file, "r") as fh:
            stand_soft = fh.readlines()
    except FileNotFoundError:
        stand_soft = set()
        print("Ошибка при работе с файлом конфигурации", file)
    return stand_soft


def fill_empty(split_list):
    lst_max = 0
    for lst in split_list:
        if len(lst) > lst_max:
            lst_max = len(lst)
    for lst in split_list:
        if len(lst) < lst_max:
            lst.append('---')
    return split_list


def get_soft_not_allowed(deb_soft, redos_soft):
    cmd_rpm = "rpm -qa | awk '{print $1}'"
    cmd_dpkg = "dpkg --list | awk 'FNR>5 {print $2}'"

    soft_not_allowed = {
        'soft_1': [],
        'soft_2': [],
        'soft_3': [],
        'soft_4': []
        }

    if os.path.exists('/usr/bin/dpkg'):
        soft_installed = os.popen(cmd_dpkg).readlines()
        stand_soft = open_soft_list(deb_soft)

    elif os.path.exists('/usr/bin/rpm'):
        soft_installed = os.popen(cmd_rpm).readlines()
        stand_soft = open_soft_list(redos_soft)

    stand_soft = {value.strip() for value in stand_soft}
    soft_installed = {value.strip() for value in soft_installed}

    rez_soft = list(soft_installed - stand_soft)

    if rez_soft != []:
        split_list = foo_split_list(rez_soft, wanted_parts=4)
        split_list = fill_empty(split_list)

        soft_not_allowed['soft_1'] = split_list[0]
        soft_not_allowed['soft_2'] = split_list[1]
        soft_not_allowed['soft_3'] = split_list[2]
        soft_not_allowed['soft_4'] = split_list[3]
    else:
        soft_not_allowed['soft_1'] = ['отсутствует']
        soft_not_allowed['soft_2'] = ['отсутствует']
        soft_not_allowed['soft_3'] = ['отсутствует']
        soft_not_allowed['soft_4'] = ['отсутствует']

    return soft_not_allowed
