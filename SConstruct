import saliweb.build

vars = Variables('config.py')
env = saliweb.build.Environment(vars, ['conf/live.conf'], service_module='evaluation')
Help(vars.GenerateHelpText(env))

env.InstallAdminTools()

Export('env')
SConscript('backend/evaluation/SConscript')
SConscript('frontend/evaluation/SConscript')
SConscript('html/SConscript')
SConscript('test/SConscript')
