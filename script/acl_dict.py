import re
import os
from pathlib import Path
from collections import OrderedDict


def file_exist(files):
    for file in files:
        if not os.path.exists(file):
            return False
    return True


def dict_access(file):
    title_obj, title_acl = {}, {}
    coment_rj = re.compile(r'^\#|^\s*\#|^\s*\n')
    title_rj = re.compile(r'\[(.+)\]')
    acl_rj = re.compile(r'\d{3}|-w')

    with open(file, 'r') as access_file:
        for i in access_file.readlines():
            if coment_rj.search(i):
                continue
            elif title_rj.search(i):
                key = title_rj.search(i).group()
                title_obj.update({key: []})
                if len(acl_rj.findall(i)) < 2:
                    title_acl.update({key: [''] + acl_rj.findall(i)})
                else:
                    title_acl.update({key: acl_rj.findall(i)})
            else:
                title_obj[key].append(re.sub("^\s+|\n|\r|\s+$|/$", '', i))
    return title_obj, title_acl


def priv_file(file):
    if os.path.exists(file):
        return oct(os.stat(file)[0])[-3:]
    else:
        return None


def add_pd_dict(pd_dict, key, obj, acl_cur, acl_stan):
    pd_dict['title'].append(key)
    pd_dict['object'].append(obj)
    pd_dict['acl_cur'].append(acl_cur)
    pd_dict['acl_stan'].append(acl_stan)


def add_pd_dict_root(pd_dict_root, key, obj, owner, group):
    pd_dict_root['title_root'].append(key)
    pd_dict_root['object_root'].append(obj)
    pd_dict_root['owner'].append(owner)
    pd_dict_root['group'].append(group)


def compare_acl(pd_dict, key, obj, acl_cur, acl_stan):
    acl_cur_rj = re.compile(r'6|7')
    if acl_cur != acl_stan:
        if acl_stan == '-w':
            if acl_cur_rj.search(acl_cur[1:]):
                add_pd_dict(pd_dict, key, obj, acl_cur, acl_stan)
        else:
            add_pd_dict(pd_dict, key, obj, acl_cur, acl_stan)


def compare_root(pd_dict_root, key, obj):
    try:
        owner = Path(obj).owner()
        group = Path(obj).group()
    except KeyError:
        owner = 'unknow'
        group = 'unknow'

    if owner != 'root' or group != 'root':
        add_pd_dict_root(pd_dict_root, key, obj, owner, group)


def get_pd_dict(title_obj, title_acl):
    pd_dict = {
        'title': [],
        'object': [],
        'acl_cur': [],
        'acl_stan': []
    }

    pd_dict_root = {
        'title_root': [],
        'object_root': [],
        'owner': [],
        'group': []
    }

    for key, value in title_obj.items():
        for obj in value:
            if not os.path.exists(obj) or os.path.islink(obj):
                continue
            if os.path.isfile(obj):
                acl_cur = priv_file(obj)
                acl_stan = title_acl[key][1]
                compare_acl(pd_dict, key, obj, acl_cur, acl_stan)
                compare_root(pd_dict_root, key, obj)

            else:
                for root, dirs, files in os.walk(obj):
                    acl_cur = priv_file(root)
                    acl_stan = title_acl[key][0]
                    compare_acl(pd_dict, key, root, acl_cur, acl_stan)
                    compare_root(pd_dict_root, key, root)
                    for dir in dirs:
                        root_dir = root + '/' + dir
                        acl_cur = priv_file(root_dir)
                        acl_stan = title_acl[key][0]
                        compare_acl(pd_dict, key, root_dir, acl_cur, acl_stan)
                        compare_root(pd_dict_root, key, root_dir)
                    for file in files:
                        root_dir = root + '/' + file
                        if os.path.islink(root_dir):
                            continue
                        else:
                            acl_cur = priv_file(root_dir)
                            acl_stan = title_acl[key][1]
                            compare_acl(pd_dict, key, root_dir, acl_cur, acl_stan)
                            compare_root(pd_dict_root, key, root_dir)

    return pd_dict, pd_dict_root
