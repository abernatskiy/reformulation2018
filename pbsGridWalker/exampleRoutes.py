from os.path import expanduser, join

home = expanduser('~')
pbsGridWalker = join(home, 'pbsGridWalker')

sysEnv = join(pbsGridWalker, 'environment/os', 'gentoo.py')
pbsEnv = join(pbsGridWalker, 'environment/host', 'vacc.py')
