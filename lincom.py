import script.acl_dict as acl_dict
import connect_ssh as con_ssh
import conf_reg
from ipaddress import IPv4Address
import script.user_admin as user_admin


files = ['script/acl_dict.py',
         'config/access_2.cfg',
         'script/user_admin.py',
         'script/rem_main.py',
         'config/target_add.cfg']

headrs = [
    'Проверка прав доступа',
    'Пользователи и администраторы системы'
    ]

num_comp = 1

if not acl_dict.file_exist(files):
    print(conf_reg.RED, 'Не найден файл программы ', files, conf_reg.ENDC)
else:
    address = conf_reg.get_ipadd(files[4])
    if len(address) == 0:
        print(conf_reg.RED, 'Адреса серверов для аудита не заданы',  conf_reg.ENDC)
    else:
        conf_reg.print_start(address, headrs)

    for ipadd in address:
        try:
            if IPv4Address(ipadd).is_loopback:
                # создаем словарь с параметрами проверки из конфига
                title_obj, title_acl = acl_dict.dict_access(files[1])

                # получаем словарь для загрузки в Pandas
                pd_dict, pd_dict_root = acl_dict.get_pd_dict(title_obj, title_acl)

                # Загружаем словари в Pandas
                df_acl = conf_reg.load_to_DF(pd_dict)
                df_root = conf_reg.load_to_DF(pd_dict_root)

                # вывод на экран результатов проверки
                num_comp = conf_reg.print_rez_start(ipadd)
                num_comp =conf_reg.print_rez(headrs[0], num_comp, df_acl, df_root)

                # Получаев в словарь пользователей
                pd_users = user_admin.get_df_user()
                # Загружаем словари в Pandas
                df_users = conf_reg.load_to_DF(pd_users)
                # вывод на экран результатов проверки
                conf_reg.print_rez(headrs[1], num_comp, df_users)

                # Сохранение отчета
                conf_reg.save_csv(ipadd, df_acl, df_root, df_users)

            elif IPv4Address(ipadd).is_private:
                str_stdout = con_ssh.connect_ssh_to(ipadd, files[:-1])

                if str_stdout is None:
                    continue
                elif str_stdout.find('access_2.cfg') != -1:
                    print(conf_reg.RED, 'Не найден файл настроек на ', ipadd, conf_reg.ENDC)
                else:
                    # получаем словарь для загрузки в Pandas
                    pd_dict, pd_dict_root, pd_users = con_ssh.regular(str_stdout)

                    try:
                        # Загружаем словари в Pandas
                        df_acl = conf_reg.load_to_DF(pd_dict)
                        df_root = conf_reg.load_to_DF(pd_dict_root)

                        df_users = conf_reg.load_to_DF(pd_users)

                        # вывод на экран результатов проверки
                        num_comp = conf_reg.print_rez_start(ipadd)
                        num_comp = conf_reg.print_rez(headrs[0], num_comp, df_acl, df_root)
                        num_comp = conf_reg.print_rez(headrs[1], num_comp, df_users)

                        # Сохранение отчета
                        conf_reg.save_csv(ipadd, df_acl, df_root, df_users)

                    except ValueError:
                        print(conf_reg.RED, 'Ошибка в программе при записи в DataFrame на ', ipadd, conf_reg.ENDC)

            else:
                print(conf_reg.RED, 'Один или несколько адресов внешнии ', address, conf_reg.ENDC)
        except ValueError:
            print(conf_reg.RED, 'Один или несколько адресов заданы не верно ', address, conf_reg.ENDC)
