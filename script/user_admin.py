import pwd
import grp
import re
import os


def add_df_users(df_users, group, user, sudo, perm):
    df_users['groups'].append(group)
    df_users['users_'].append(user)
    df_users['sudoers'].append(sudo)
    df_users['perm'].append(perm)


def get_files(objects):
    file_list = []
    for obj in objects:
        if os.path.isfile(obj):
            file_list.append(obj)
        elif os.path.isdir(obj):
            for root, dirs, files in os.walk(obj):
                for file in files:
                    file_list.append(root + file)
    return file_list


def get_sudo_user(objects):
    sudo_rj2 = re.compile(r'^([%\w-]+)\s*(ALL[ALL,\=,\(,\),\:\s\w]*)\s+$')
    sudo_rj3 = re.compile(r'^%([\w-]+)')
    sudo_group = {
        'groups': [],
        'perm_g': [],
        'users_': [],
        'perm_u': []
    }

    files = get_files(objects)

    for file in files:
        with open(file, 'r') as access_file:
            for string in access_file.readlines():
                if sudo_rj2.search(string):
                    if sudo_rj3.search(string):
                        sudo_group['groups'].append(sudo_rj3.search(string).group(1))
                        sudo_group['perm_g'].append(sudo_rj2.search(string).group(2))
                    else:
                        sudo_group['users_'].append(sudo_rj2.search(string).group(1))
                        sudo_group['perm_u'].append(sudo_rj2.search(string).group(2))
    return sudo_group


def get_df_user():
    df_users = {
        'groups': [],
        'users_': [],
        'sudoers': [],
        'perm': []
    }

    objects = ['/etc/sudoers', '/etc/sudoers.d/']

    gr_admin = re.compile(r'root|wheel|\w*admin\w*|sudo|docker')

    sudo_group = get_sudo_user(objects)

    # заполняем словарь с УЗ из групп ОС
    for gr in grp.getgrall():
        if gr_admin.search(gr[0]):
            if gr[3] == []:
                add_df_users(df_users, gr[0], '-', '-', '-')
            else:
                add_df_users(df_users, gr[0], ', '.join(gr[3]), '-', '-')

    # заполняем словарь с УЗ  группами из sudoers
    for sudo_gr in sudo_group['groups']:
        index1 = None
        index2 = sudo_group['groups'].index(sudo_gr)
        for df_gr in df_users['groups']:
            if sudo_gr == df_gr:
                index1 = df_users['groups'].index(df_gr)
                df_users['sudoers'][index1] = 'sudo'
                df_users['perm'][index1] = sudo_group['perm_g'][index2]
                break
        if index1 is None:
            try:
                if grp.getgrnam(sudo_gr):
                    for gr in grp.getgrall():
                        if gr[0] == sudo_gr:
                            if gr[3] == []:
                                add_df_users(df_users, sudo_gr, '-', 'sudo', sudo_group['perm_g'][index2])
                            else:
                                add_df_users(df_users, sudo_gr, ', '.join(gr[3]), 'sudo', sudo_group['perm_g'][index2])
                            break
            except KeyError:
                add_df_users(df_users, sudo_gr + ' **not exist', '-', 'sudo', sudo_group['perm_g'][index2])

    # заполняем словарь с УЗ  пользователями из sudoers
    for sudo_u in sudo_group['users_']:
        index2 = sudo_group['users_'].index(sudo_u)
        add_df_users(df_users, '-', sudo_u, 'sudo', sudo_group['perm_u'][index2])

    # заполняем словарь с УЗ  пользователями из passwd с id начиная с 1000
    for uid in pwd.getpwall():
        if uid[2] > 999:
            index1 = None
            for list_users in df_users['users_']:
                if uid[0] in list_users:
                    index1 = uid[0]
                    break
            if index1 is None:
                add_df_users(df_users, uid[0], uid[0], '-', '-')
    return df_users
