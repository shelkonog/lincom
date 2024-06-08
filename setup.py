from cx_Freeze import setup, Executable


build_exe_options = {
    "includes": ['tabulate'],
    "include_files": ['config', 'report', 'script'],
    "zip_include_packages": ['numpy', "numpy.libs", 'pandas',
                             'paramiko', "email", 'rem_main', "nacl",
                             'connect_ssh', 'conf_reg', 'acl_dict'],
}

setup(
    name="lincom",
    version="0.1",
    description="Compliance Linux",
    options={"build_exe": build_exe_options},
    executables=[Executable('lincom.py')],
)
