import acl_dict as acl_dict
import user_admin as user_admin
import comp_conf as comp_conf


files = ['/tmp/acl_dict.py',
         '/tmp/access_2.cfg',
         '/tmp/user_admin.py',
         '/tmp/conf_srv.jsn',
         '/tmp/comp_conf.py']

if not acl_dict.file_exist(files):
    print('FileNotExist')
else:
    # создаем словарь с параметрами проверки из конфига
    title_obj, title_acl = acl_dict.dict_access(files[1])

    # печатаем словарь для передачи  по ssh с удаленной машины
    print(acl_dict.get_pd_dict(title_obj, title_acl))
    print(user_admin.get_df_user(), user_admin.get_user_pass())

    for rez_i in comp_conf.rez_comp_conf(files[3]):
        print(rez_i)
