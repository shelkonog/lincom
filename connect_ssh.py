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

    acl_dict = None
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
                acl_dict = line

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


def regular(str):
    pd_dict = {
        'title': [],
        'object': [],
        'acl_cur': [],
        'acl_stan': []
    }

    pd_dict_root = {
        'title': [],
        'object': [],
        'owner': [],
        'group': []
    }

    df_users = {
        'groups': [],
        'users_': [],
        'sudoers': [],
        'perm': []
    }

    split = re.compile(r"\{[^\}]*\}")
    rj = re.compile(r"\'([^\']*)\'")

    try:
        str1 = split.findall(str)[0]
        str2 = split.findall(str)[1]
        str3 = split.findall(str)[2]

        list1 = rj.findall(str1)
        list2 = rj.findall(str2)
        list3 = rj.findall(str3)
    except IndexError:
        list1, list2, list3 = [], [], []
        print(conf_reg.RED, f'Ошибка получения данных с удаленного хоста', conf_reg.ENDC)

    for i in list1:
        if i in pd_dict:
            key = i
        else:
            pd_dict[key].append(i)

    for i in list2:
        if i in pd_dict_root:
            key = i
        else:
            pd_dict_root[key].append(i)

    for i in list3:
        if i in df_users:
            key = i
        else:
            df_users[key].append(i)

    return pd_dict, pd_dict_root, df_users
