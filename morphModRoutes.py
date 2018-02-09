from os.path import join, expanduser
morphModPath = join(expanduser('~'), 'morphMod')
import sys
sys.path.append(join(morphModPath))
import pbsGridWalker.routes as rt

involvedGitRepositories = {'evs': join(morphModPath, 'evs'),
                           'arrowbots': join(morphModPath, 'arrowbots'),
                           'pbsGridWalker': join(morphModPath, 'pbsGridWalker'),
                           'morphMod': morphModPath}
randSeedFile = join(involvedGitRepositories['pbsGridWalker'], 'seedFiles', 'randints1501268598.dat')
evsExecutable = join(morphModPath, 'evs', 'evsServer.py')
arrowbotsExecutable = join(morphModPath, 'arrowbots', 'arrowbotEvaluator')
