import json
import os
import re


def clear_list(rez_comp):
    for rez_comp_i in rez_comp[1]:
       rez_comp[0][rez_comp_i] = []


def write_list(rez_comp, key_cfg_stand, rez, key_cfg):
    rez_comp[0][rez_comp[1][0]].append(key_cfg[0])
    rez_comp[0][rez_comp[1][1]].append(key_cfg[1])
    rez_comp[0][rez_comp[1][2]].append(key_cfg_stand)
    rez_comp[0][rez_comp[1][3]].append(rez)


def get_logrotate(key):
    file_logrotate = '/etc/logrotate.conf'
    period = ['daily', 'weekly', 'monthly']
    logrotate_real, params = [], []
    count_rotate_re = re.compile(r"rotate\s*\d")
    if not os.path.exists(file_logrotate):
        logrotate_real = None
    else:
        ls = os.popen(key).readlines()
        log_conf_files = [line.strip() for line in ls]
        count_rot = ''
        params_str = ''
        if file_logrotate in key:
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


def get_conf(key, name_conf):
    list_conf = []
    if name_conf == 'logrotate_conf':
        list_conf = get_logrotate(key)
    else:
        list_serv = os.popen(key).readlines()
        list_serv = [line.strip().split() for line in list_serv]
        for key_cfg in list_serv:
            if name_conf == 'journald_conf':
                key_cfg = key_cfg[0].split('=')
            if (len(key_cfg) == 3) and key_cfg[1] == '=':
                key_cfg.remove('=')
            if (len(key_cfg) == 2):
                list_conf.append(key_cfg.copy())
    return list_conf


def get_comp_conf(stand_conf, key, value):
    name_conf = value[2]

    clear_list(value)

    list_serv = get_conf(key, name_conf)

    for key_cfg in list_serv:
        if (len(key_cfg) == 2) and stand_conf is not None:
            if key_cfg[0] in stand_conf[name_conf]:
                stand_rez = stand_conf[name_conf][key_cfg[0]]
                if key_cfg[1] != stand_rez:
                    write_list(value, stand_rez, 'no', key_cfg)
                else:
                    write_list(value, stand_rez, 'pass', key_cfg)
    '''for params, params_value in stand_conf[name_conf].items():
        if params not in value[0][value[1][0]]:
            key_cfg = []
            key_cfg.append(params)
            key_cfg.append('---')
            write_list(value, params_value, 'no', key_cfg)'''

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

    cmd_syslog_ng = "cat /etc/syslog-ng/syslog-ng.conf | awk '/^destin/ {gsub(/[\{,\},\;,\"]/, \"\", $0) ;print $2\" \"$3}'"
    cmd_sudoers_log = "cat /etc/sudoers | awk -F= '/logfile/ {gsub(/Defaults/, "",$1); gsub(/\s/, "",$1); print $1" "$2}'"

    service_conf = {
        'sshd -T': [sshd_conf, ['key_ssh', 'value_ssh', 'value_stand_ssh', 'status_ssh'], 'sshd_conf'],
        "cat /etc/audit/auditd.conf": [auditd_conf, ['key_audit', 'value_audit', 'value_stand_audit', 'status_audit'], 'auditd_conf'],
        "cat /etc/systemd/journald.conf | grep -v '^$'": [journald_conf, ['key_journal', 'value_journal', 'value_stand_journal', 'status_journal'], 'journald_conf'],
        "cat /etc/rsyslog.conf | grep -v '^#\|^$\|^\$'": [rsyslog_conf, ['key_rsyslog', 'value_rsyslog', 'value_stand_rsyslog', 'status_rsyslog'], 'rsyslog_conf'],
        "cat /etc/rsyslog.d/* | grep -v '^#\|^$\|^\$'": [rsyslog_conf, ['key_rsyslog', 'value_rsyslog', 'value_stand_rsyslog', 'status_rsyslog'], 'rsyslog_conf'],
        cmd_syslog_ng: [rsyslog_conf, ['key_rsyslog', 'value_rsyslog', 'value_stand_rsyslog', 'status_rsyslog'], 'rsyslog_conf'],
        "cat /etc/logrotate.conf | grep -v '^#\|^$'": [logrotate_conf, ['key_logrotate', 'value_logrotate', 'value_stand_logrotate', 'status_logrotate'], 'logrotate_conf'],
        "cat /etc/logrotate.d/* | grep -v '^#\|^$'": [logrotate_conf, ['key_logrotate', 'value_logrotate', 'value_stand_logrotate', 'status_logrotate'], 'logrotate_conf']
    }

    for key, value in service_conf.items():
        yield get_comp_conf(stand_conf, key, value)
