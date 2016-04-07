#!C:/python2.7/python.exe

import shutil
import os
import sys
import subprocess
import argparse

if os.name == 'nt':
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]),r"tools/pylibs/"))
    import winenv

def parse_option():

    parser = argparse.ArgumentParser(description='CMake Test Compile Script for WIN')
    g1 = parser.add_argument_group('compilation options')
    g1.add_argument('-x64', action='store_true',  help='for amd64.')
    g1.add_argument('-release', action='store_true', 
            help='compiel with release mode')
    g1.add_argument('-l', '--list', action='store_true', 
            help='the vaild targets for make/nmake command')
    g1.add_argument('target', action='store', nargs='*', 
            help='compile target name. by default: nmake install.')


    g2 = parser.add_argument_group('cmake options')
    g2.add_argument('-t', '--create',choices={'makefile', 'sln'}, default='makefile', 
             nargs='?', 
            help = 'create new CMake Cache with type makefile or VS sln')
    g2.add_argument('-r', '--rebuild', action='store_true',  
            help='rebuilt CMake Cache')
    g2.add_argument('-f', '--fastrebuild', action='store_true',  
            help='fast rebuilt CMake Cache')
    g2.add_argument('-R', '--rebuild-all', action='store_false',
            help= 'rebuilt entire project')
    g2.add_argument('-c', '--no-colored', action='store_true',
            help= 'disable cmake colored output.')

    g3 = parser.add_argument_group('Generating Update package options')
    g3.add_argument('-u', '--generate-update-package', action = 'store_true',
            help = 'generate update package')

    args = parser.parse_args()

    #Namespace(list, rebuild, rebuild_all, release, target, x64)
    return args

path = os.path
#call=subprocess.call

def call(cmd_str, shell = False):

    if shell:
        rc = subprocess.call(cmd_str, shell = True)
    else:
        import shlex
        rc = subprocess.call(shlex.split(cmd_str, posix=False), shell = False)

    if rc != 0:
        print "-- run command: [%s] failed. " % (cmd_str)
        sys.exit(1)

if __name__=="__main__":
    
    ## when I run the script on console with command as below.
    ##      $ python xxx/build/compile_win.py
    ## This statment  'cwd = path.dirname(sys.argv[0])' return incorrent directory
    ## 
    ## so, here I use __file__ to locate the project diretory.
    cwd = path.dirname(path.realpath(__file__))
    _CMAKETEST_PROJCET_DIR_ = path.join(cwd, '..')
    winenv.debug(_CMAKETEST_PROJCET_DIR_)

    args =  parse_option()
    print args
    
    target_arch = 'x64' if args.x64 else 'x86'
    winenv.setup_env(target_arch)

    ## check build directory.
    build_type  = 'release' if args.release else 'debug'
    s = 'Win64' if args.x64 else 'Win32'
    build_dir = '%s-%s' % (s, build_type)
    ##    create dir 
    compile_dir = path.join(cwd,build_dir)
    if not path.exists(compile_dir):
        os.mkdir(compile_dir)
    
    ## get CMake path
    cmake =  path.join(cwd, r'tools\cmake_win\bin\cmake.exe')
    if not path.exists(cmake):
        raise "CMake is not existing"
    
    ## change cwd to build directory
    build_cwd = path.join(cwd, build_dir)
    os.chdir(build_cwd)

    ## - helper func: create cmake cache
    def create_cache(target_, is_release = False, no_colored_output = False):
        
        bt = '-DCMAKE_BUILD_TYPE=Release' if is_release else ""
        bt += ' -DCMAKE_COLOR_MAKEFILE=OFF' if no_colored_output else "" 

        if target_ == 'makefile':
            cmd = '%s -G "NMake Makefiles" %s %s' % (cmake, bt, _CMAKETEST_PROJCET_DIR_)
        else:
            cmd = '%s %s %s' % (cmake, bt, _CMAKETEST_PROJCET_DIR_)
        call(cmd, shell=True)
    
    ##- helper func: clear cmake cache
    def clear_cache(x):
        #shutil.rmtree(x)
        for f in os.listdir(x):
            if path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
            
    ##+  fast rebuild cmake cache
    if args.fastrebuild:
        clear_cache('.')
        create_cache(args.create, args.release, args.no_colored)
        sys.exit(0)

    ##+  rebuild cmake cache
    if args.rebuild:
        clear_cache('.')
        extlib_path = os.path.join(_CMAKETEST_PROJCET_DIR_,'extlib', s)
        for x in ["include", "bin", "lib"]:
            p = os.path.join(extlib_path, x)
            if os.path.exists(p):
                shutil.rmtree(p)
            create_cache(args.create, args.release, args.no_colored)
        sys.exit(0)

    ##+  list make targets
    if args.list:
        if not path.exists('Makefile'):
            create_cache(args.create, args.release, args.no_colored)
        call('nmake help')
        sys.exit(0)

    ## do nmake
    if not path.exists('CMakeCache.txt'):
        create_cache(args.create, args.release, args.no_colored)
           
    if args.target:
        call('nmake ' +  ' '.join(args.target))
        
    ## if none target was specified, exect 'make install' by default.
    elif path.exists('Makefile'):
        call('nmake')
        call('nmake install')
    
