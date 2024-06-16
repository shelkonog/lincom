import paramiko
import re
import os
import getpass
import conf_reg


def connect_ssh_to(address, files):
    '''login = 'vagrant'
    passwd = 'vagrant'
    '''

    print()
    print(conf_reg.ENDC, f'Введите параметры учетной записи для доступа к {address} ')
    print('Username: ', end='')
    login = input()
    passwd = getpass.getpass()
    print(conf_reg.ENDC)

    acl_dict = []
    with paramiko.SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        try:
            ssh_client.connect(hostname=address, port=22,
                                username=login, password=passwd,
                                timeout=15)

            sftp = ssh_client.open_sftp()
            for file in files:
                sftp.put(os.path.realpath(file), re.sub(r'config/|script/', '/tmp/', file))
            sftp.close()

            stdin, stdout, stderr = ssh_client.exec_command('sudo -S python3 /tmp/rem_main.py', get_pty=True)

            stdin.write(passwd + '\n')
            stdin.flush()

            for line in stderr:
                print(conf_reg.RED, f'{address}: {line}', conf_reg.ENDC)

            for line in stdout:
                acl_dict.append(line)

            for file in files:
                ssh_client.exec_command('rm ' + re.sub(r'config/|script/', '/tmp/', file))

        except TimeoutError:
            print(conf_reg.RED, f'Истек таймаут подключения к {address}', conf_reg.ENDC)
            acl_dict = None

        except paramiko.ssh_exception.BadAuthenticationType:
            print(conf_reg.RED, f'Не удачная попытка аутентификации к {address}', conf_reg.ENDC)
            acl_dict = None

        except paramiko.ssh_exception.AuthenticationException:
            print(conf_reg.RED, f'Не удачная попытка аутентификации к {address}', conf_reg.ENDC)
            acl_dict = None

        except paramiko.ssh_exception.NoValidConnectionsError:
            print(conf_reg.RED, f'Не удачная попытка подключения к {address}', conf_reg.ENDC)
            acl_dict = None

        except FileNotFoundError:
            print(conf_reg.RED, f'Не удалось найти файл {file} для копирования на {address}', conf_reg.ENDC)
            acl_dict = None

        finally:
            ssh_client.close()

    return acl_dict


def create_dict(list, dict1):
    key = list[0]
    for i in list:
        if i in dict1:
            key = i
        else:
            try:
                dict1[key].append(i)
            except KeyError:
                print(conf_reg.RED, f'Ошибка при форматировании данных', conf_reg.ENDC)
    return dict1


def regular(lst_dict):

    str_rez = str(lst_dict)

    list_dict = []

    dict_os_info = {
        'name_title': [],
        'params': [],
        'params_empty1': [],
        'params_empty2': []
        }
    list_dict.append(dict_os_info)

    pd_dict = {
        'title': [],
        'object': [],
        'acl_cur': [],
        'acl_stan': []
    }
    list_dict.append(pd_dict)

    pd_dict_root = {
        'title_root': [],
        'object_root': [],
        'owner': [],
        'group': []
    }
    list_dict.append(pd_dict_root)

    df_users = {
        'groups': [],
        'users_': [],
        'sudoers': [],
        'perm': []
    }
    list_dict.append(df_users)

    pd_user_pass = {
        'user_': [],
        'pass_change': [],
        'max_time_change': [],
        'status': []
    }
    list_dict.append(pd_user_pass)

    sshd_conf = {
            'key_ssh': [],
            'value_ssh': [],
            'value_stand_ssh': [],
            'status_ssh': []
        }
    list_dict.append(sshd_conf)

    auditd_conf = {
            'key_audit': [],
            'value_audit': [],
            'value_stand_audit': [],
            'status_audit': []
    }
    list_dict.append(auditd_conf)

    journald_conf = {
            'key_journal': [],
            'value_journal': [],
            'value_stand_journal': [],
            'status_journal': []
    }
    list_dict.append(journald_conf)

    rsyslog_conf = {
                'key_rsyslog': [],
                'value_rsyslog': [],
                'value_stand_rsyslog': [],
                'status_rsyslog': []
        }
    list_dict.append(rsyslog_conf)

    logrotate_conf = {
                'key_logrotate': [],
                'value_logrotate': [],
                'value_stand_logrotate': [],
                'status_logrotate': []
        }
    list_dict.append(logrotate_conf)

    split = re.compile(r"\{[^\}]*\}")
    rj = re.compile(r"\'([^\']*)\'")
    list_n = []

    try:
        count_dict = len(split.findall(str_rez))
        for i in range(count_dict):
            str_split = split.findall(str_rez)[i]
            list_n.append(rj.findall(str_split))

    except IndexError:
        list_n[i] = []
        print(conf_reg.RED, f'Ошибка получения данных с удаленного хоста', conf_reg.ENDC)

    for j in range(len(list_n)):
        for dict_conf in list_dict:
            if list_n[j][0] in dict_conf:
                break
        dict_conf = create_dict(list_n[j], dict_conf)

    return list_dict
