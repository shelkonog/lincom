import script.acl_dict as acl_dict
import connect_ssh as con_ssh
import conf_reg
from ipaddress import IPv4Address
import script.user_admin as user_admin
import script.comp_conf as comp_conf


files = ['script/acl_dict.py',
         'config/acl_dir.jsn',
         'config/conf_srv.jsn',
         'script/comp_conf.py',
         'script/user_admin.py',
         'script/rem_main.py',
         'config/target_add.cfg']

headrs = [
    'Данные о хосте и ОС',
    'Права доступа к файлам',
    'Владельцы файлов',
    'Пользователи и администраторы',
    'Смена парольной информации',
    'Конфигурация sshd',
    'Конфигурация auditd',
    'Конфигурация journald'
    ]

list_dict = []

if not acl_dict.file_exist(files):
    print(conf_reg.RED, 'Не найден файл программы ', files, conf_reg.ENDC)

else:
    address = conf_reg.get_ipadd(files[-1])
    if len(address) == 0:
        print(conf_reg.RED, 'Адреса серверов для аудита не заданы',  conf_reg.ENDC)
    else:
        conf_reg.print_start(address, headrs)

    if conf_reg.json_decod_er(files[2]):
        print(conf_reg.RED, 'Ошибка в конфигурационном файле json', files[2], conf_reg.ENDC)

    for ipadd in address:
        try:
            if IPv4Address(ipadd).is_loopback:
                # получаем словарь для загрузки в Pandas
                list_dict.append(acl_dict.get_os_info())
                list_acl_dir_root = acl_dict.get_acl_dir_root(files[1])
                for dict1 in list_acl_dir_root:
                    list_dict.append(dict1)
                # Получаев в словарь пользователей
                list_dict.append(user_admin.get_df_user())
                list_dict.append(user_admin.get_user_pass())

                for dict1 in comp_conf.rez_comp_conf(files[2]):
                    list_dict.append(dict1)

                try:
                    # Загружаем словари в Pandas
                    for i in range(len(list_dict)):
                        df_rez = conf_reg.load_to_DF(list_dict[i])
                        # вывод на экран результатов проверки
                        conf_reg.print_rez(headrs[i], i, df_rez)
                        # Сохранение отчета
                        conf_reg.save_csv(ipadd, i, df_rez)
                except ValueError:
                    print(conf_reg.RED, 'Ошибка в программе при записи в DataFrame на ', ipadd, conf_reg.ENDC)

            elif IPv4Address(ipadd).is_private:
                str_stdout = con_ssh.connect_ssh_to(ipadd, files[:-1])

                if str_stdout is None:
                    continue
                elif "FileNotExist" in str_stdout:
                    print(conf_reg.RED, 'Не найден файл настроек на ', ipadd, conf_reg.ENDC)
                elif "json.JSONDecodeError" in str_stdout:
                    print(conf_reg.RED, 'Ошибка в конфигурационном файле json', ipadd, conf_reg.ENDC)
                else:
                    # получаем словарь для загрузки в Pandas
                    list_dict = con_ssh.regular(str_stdout)

                    try:
                        conf_reg.print_rez_start(ipadd)
                        # Загружаем словари в Pandas
                        for i in range(len(list_dict)):
                            df_rez = conf_reg.load_to_DF(list_dict[i])
                            # вывод на экран результатов проверки
                            conf_reg.print_rez(headrs[i], i, df_rez)
                            # Сохранение отчета
                            conf_reg.save_csv(ipadd, i, df_rez)

                    except ValueError:
                        print(conf_reg.RED, 'Ошибка в программе при записи в DataFrame на ', ipadd, conf_reg.ENDC)

            else:
                print(conf_reg.RED, 'Один или несколько адресов внешнии ', address, conf_reg.ENDC)
        except ValueError:
            print(conf_reg.RED, 'Один или несколько адресов заданы не верно ', address, conf_reg.ENDC)
