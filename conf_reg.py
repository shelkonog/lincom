import re
import pandas as pd

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
    acl = re.compile('acl_cur')
    owner = re.compile('owner')
    admin = re.compile('perm')
    df = pd.DataFrame(pd_dict)
    if acl.search(str(pd_dict.keys())):
        df.columns = ['Категория', 'Объект', 'Текущие', 'Стандартные']
    elif owner.search(str(pd_dict.keys())):
        df.columns = ['Категория', 'Объект', 'Владелец', 'Группа']
    elif admin.search(str(pd_dict.keys())):
        df.columns = ['Группа', 'Пользователи', 'Sudoers', 'Права']
    return df


def print_start(address, headr):
    print()
    print(ENDC, f'Внутренний аудит настроек серверов : {YELLOW} {address}')
    print(ENDC, f'Перечень проверок : {YELLOW} {headr}', ENDC)


def print_rez_start(ipadd):
    print()
    print(ENDC, f'Результаты проверки: {YELLOW} {ipadd}')
    num_comp = 1
    return num_comp


def print_rez(headr, num_comp, *df):
    print(ENDC, f'---{headr}---')
    for df_i in df:
        print(ENDC, f'Проверка № :   {num_comp}')
        if not df_i.empty:
            print(YELLOW, df_i, ENDC)
            print()
        else:
            print(YELLOW, 'Нет данных', ENDC)
        num_comp += 1
    return num_comp


def save_csv(ipadd, *df):
    i = 0
    pd_empty = {
        '#####': [],
        '######': [],
        '#######': [],
        '########': []
    }
    df_empty = pd.DataFrame(pd_empty)
    try:
        for df_i in df:
            if i == 0:
                df_i.to_csv('report/' + ipadd + '_.csv')
            else:
                df_empty.to_csv('report/' + ipadd + '_.csv', mode='a')
                df_i.to_csv('report/' + ipadd + '_.csv', mode='a')
            i += 1
    except PermissionError:
        print(RED, f'Недостаточно прав для операции сохранения отчета {ipadd}', ENDC)
