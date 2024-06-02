import json
import os
import re
from pathlib import Path
import time


def file_exist(files):
    for file in files:
        if not os.path.exists(file):
            return False
    return True


def priv_file(file):
    if os.path.exists(file):
        return oct(os.stat(file)[0])[-3:]
    else:
        return None


def get_acl_stan(acl: str):
    acl_lst = acl.split(',')
    if len(acl_lst) < 2:
        acl_lst.append(acl_lst[0])
    for i in range(len(acl_lst)):
        acl_lst[i] = acl_lst[i].strip()
    print(acl_lst)
    return acl_lst


def add_pd_dict(acl_dir_root, title, obj, acl_cur, acl_stan):
    if 'acl_cur' in acl_dir_root:
        acl_dir_root['title'].append(title)
        acl_dir_root['object'].append(obj)
        acl_dir_root['acl_cur'].append(acl_cur)
        acl_dir_root['acl_stan'].append(acl_stan)
    elif 'owner' in acl_dir_root:
        acl_dir_root['title_root'].append(title)
        acl_dir_root['object_root'].append(obj)
        acl_dir_root['owner'].append(acl_cur)
        acl_dir_root['group'].append(acl_stan)
    elif 'name_title' in acl_dir_root:
        acl_dir_root['name_title'].append(title)
        acl_dir_root['params'].append(obj)
        acl_dir_root['params_empty1'].append(acl_cur)
        acl_dir_root['params_empty2'].append(acl_stan)


def compare_acl(acl_dir_root, title, obj, acl_cur, acl_stan):
    acl_cur_rj = re.compile(r'6|7')
    if acl_cur != acl_stan:
        if acl_stan == '-w':
            if acl_cur_rj.search(acl_cur[1:]):
                add_pd_dict(acl_dir_root, title, obj, acl_cur, acl_stan)
        else:
            add_pd_dict(acl_dir_root, title, obj, acl_cur, acl_stan)


def compare_root(pd_dict_root, key, obj):
    try:
        owner = Path(obj).owner()
        group = Path(obj).group()
    except KeyError:
        owner = 'unknow'
        group = 'unknow'

    if owner != 'root' or group != 'root':
        add_pd_dict(pd_dict_root, key, obj, owner, group)


def get_acl_dir_root(file):
    try:
        with open(file, "r") as fh:
            stand_conf = json.load(fh)
    except json.JSONDecodeError:
        stand_conf = {}
        print("json.JSONDecodeError")

    acl_dir_root = []

    pd_dict = {
            'title': [],
            'object': [],
            'acl_cur': [],
            'acl_stan': []
    }
    acl_dir_root.append(pd_dict)

    pd_dict_root = {
        'title_root': [],
        'object_root': [],
        'owner': [],
        'group': []
    }
    acl_dir_root.append(pd_dict_root)

    for title, acl_dir in stand_conf.items():
        for acl, dir_lst in acl_dir.items():
            acl_lst_stan = get_acl_stan(acl)
            if not type(dir_lst) is list:
                dir_lst = dir_lst.split()
            for obj in dir_lst:
                if not os.path.exists(obj) or os.path.islink(obj):
                    continue
                elif os.path.isfile(obj):
                    acl_cur = priv_file(obj)
                    acl_stan = acl_lst_stan[1]
                    compare_acl(acl_dir_root[0], title, obj, acl_cur, acl_stan)
                    compare_root(acl_dir_root[1], title, obj)
                else:
                    for root, dirs, files in os.walk(obj):
                        acl_cur = priv_file(root)
                        acl_stan = acl_lst_stan[0]
                        compare_acl(acl_dir_root[0], title, root, acl_cur, acl_stan)
                        compare_root(acl_dir_root[1], title, root)
                        for dir in dirs:
                            root_dir = root + '/' + dir
                            acl_cur = priv_file(root_dir)
                            acl_stan = acl_lst_stan[0]
                            compare_acl(acl_dir_root[0], title, root_dir, acl_cur, acl_stan)
                            compare_root(acl_dir_root[1], title, root_dir)
                        for file in files:
                            root_dir = root + '/' + file
                            if os.path.islink(root_dir):
                                continue
                            else:
                                acl_cur = priv_file(root_dir)
                                acl_stan = acl_lst_stan[1]
                                compare_acl(acl_dir_root[0], title, root_dir, acl_cur, acl_stan)
                                compare_root(acl_dir_root[1], title, root_dir)
    return acl_dir_root


def get_os_info():

    dict_os_info = {
        'name_title': [],
        'params': [],
        'params_empty1': [],
        'params_empty2': []
    }

    lst_cmd_os = {
        'Hostname: ': "hostname",
        'If address: ': "ip -br a | awk '/UP/ {print $1 FS $3}'",
        'OS info: ': "cat /etc/os-release | awk -F= '/PRETTY_NAME/ {print $2}'"
    }

    for title, cmd_os in lst_cmd_os.items():
        os_info = os.popen(cmd_os).readlines()
        for value in os_info:
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            add_pd_dict(dict_os_info, title, value, "", "")

    files = ["/var/log/apt/history.log", "/var/log/yum.log"]
    for file in files:
        if os.path.exists(file):
            laste_update = time.ctime(os.stat(file)[8])
            add_pd_dict(dict_os_info, "Last update OS: ", laste_update, "", "")
    return dict_os_info
