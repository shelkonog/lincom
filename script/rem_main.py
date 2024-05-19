import acl_dict as acl_dict
import user_admin as user_admin


files = ['/tmp/acl_dict.py', '/tmp/access_2.cfg', '/tmp/user_admin.py']

if not acl_dict.file_exist(files):
    print('Не найден файл программы access_2.cfg')
else:
    # создаем словарь с параметрами проверки из конфига
    title_obj, title_acl = acl_dict.dict_access(files[1])

    # печатаем словарь для передачи  по ssh с удаленной машины
    print(acl_dict.get_pd_dict(title_obj, title_acl), user_admin.get_df_user())
