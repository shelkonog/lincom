import re
import json
import pandas as pd
from tabulate import tabulate

# коды цветов для печати
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
PURPLE = '\033[35m'
ENDC = '\033[m'


def get_ipadd(file):
    coment_rj = re.compile(r'^\#|^\s*\#|^\s*\n')
    ipaddress_rj = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    ip_list = []
    with open(file, 'r') as cfg_file:
        for i in cfg_file.readlines():
            if coment_rj.search(i):
                continue
            if ipaddress_rj.search(i):
                ip_list.append(ipaddress_rj.search(i).group())
    return ip_list


def load_to_DF(pd_dict):
    key_srv_conf = ['key_ssh', 'key_audit', 'key_journal']
    df = pd.DataFrame(pd_dict)
    key_list = list(pd_dict.keys())
    if 'acl_cur' in key_list:
        df.columns = ['Категория', 'Объект', 'Текущие', 'Стандартные']
    elif 'name_title' in key_list:
        df.columns = ['Параметр', 'Значение', '', '']
    elif 'owner' in key_list:
        df.columns = ['Категория', 'Объект', 'Владелец', 'Группа']
    elif 'perm' in key_list:
        df.columns = ['Группа', 'Пользователи', 'Sudoers', 'Права']
    elif 'pass_change' in key_list:
        df.columns = ['Пользователь', 'Дата смены', 'След. смена', 'Статус']
    elif key_list[0] in key_srv_conf:
        df.columns = ['Параметр', 'Текущий', 'Стандартный', 'Статус']
        df.iloc[:, [3]] = df.iloc[:, [3]].replace('no', RED+'no pass'+YELLOW)
        df.iloc[:, [3]] = df.iloc[:, [3]].replace('pass', GREEN+'pass'+YELLOW)
    return df


def print_start(address, headr):
    print()
    print(ENDC, f'Внутренний аудит настроек серверов : {YELLOW} {address}')
    print(ENDC, f'Перечень проверок : {YELLOW} {headr}', ENDC)


def print_rez_start(ipadd):
    print()
    print(ENDC, f'Результаты проверки: {YELLOW} {ipadd}')


def print_rez(headr, num_comp, *df):
    print(ENDC, f'---{headr}---')
    for df_i in df:
        print(ENDC, f'Проверка № :   {num_comp + 1}')
        if not df_i.empty:
            print(YELLOW, tabulate(df_i, headers='keys', tablefmt='psql'), ENDC)
            print()
        else:
            print(YELLOW, 'Нет данных', ENDC)


def save_csv(ipadd, i, *df):
    pd_empty = {
        '#####': [],
        '######': [],
        '#######': [],
        '########': []
    }
    df_empty = pd.DataFrame(pd_empty)
    try:
        for df_i in df:
            if i == 1:
                df_i.to_csv('report/' + ipadd + '_.csv')
            else:
                df_empty.to_csv('report/' + ipadd + '_.csv', mode='a')
                df_i.to_csv('report/' + ipadd + '_.csv', mode='a')
    except PermissionError:
        print(RED, f'Недостаточно прав для операции сохранения отчета {ipadd}', ENDC)


def json_decod_er(file):
    try:
        with open(file, "r") as fh:
            json.load(fh)
    except json.JSONDecodeError:
        return True
    return False
