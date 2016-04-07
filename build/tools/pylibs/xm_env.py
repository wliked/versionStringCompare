import os,sys
class xmenv:
    def is_x64(self): pass
    def shortosname(self): pass
    def osname(self): pass
    def setup_env(self): pass
    def cmake_bin(self): pass
    def doxgen_bin(self): pass
    def swig_bin(self): pass
    def make_bin(self): pass

if os.name == 'nt':
    import winenv

cwd=os.path.dirname(sys.argv[0])
class xm_win_env(xmenv):
    def is_x64(self):
        return winenv.is_win64()

    def make_bin(self):
        return 'nmake'

    def shortname(self):
        if self.is_x64():
            return 'WIN64'  
        else:
            return "WIN32"

    def shortosname(self):
        return self.shortname()

    def osname(self):
        if self.is_x64():
            return 'WIN64'  
        else:
            return "WIN32"

    def setup_env(self, target_arch):
        winenv.setup_env(target_arch)
        
    def cmake_bin(self, cwd="."):
        CMAKE_BIN_ =  os.path.join(cwd, r'tools\cmake_win\bin\cmake.exe')
        return CMAKE_BIN_

    def doxgen_bin(self):
        doxgen_bin =  os.path.join(cwd, r'tools\doxgen.exe')
        return doxgen_bin

    def swig_bin(self):
        swig_bin =  os.path.join(cwd, r'tools\swig.exe')
        return swig_bin

    def debug(self, s):
        sys.stdout.write("DEBUG: %s \n" % (s))

import subprocess

def runcmd(cmd):
     p = subprocess.Popen(cmd, stdin=None,
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT,
            shell=True) 
     p.wait()
     return (p.returncode, p.stdout.read())

class xm_linux_env(xmenv):
    def __init__(self):
        self.m = {}
    def is_x64(self):
        re, c  = runcmd('uname -p')
        if re == 0 and c.strip() == 'x86_64':
            return True
        return False

    def __get_os_info(self):
        re, c  = runcmd('lsb_release -a')
        if re == 0:
            for l in c.splitlines()[1:]:
                key,value = l.split(":")  
                self.m[key.strip()] = value.strip()

    def shortname(self):
        if not self.m:
            self.__get_os_info()
            
        c = self.m['Description']
        s = [w[0].upper() for w in c.split(' ') if w.isalpha()]
        n = ''.join(s[0:4])
        return n

    def shortosname(self):
        if not self.m:
            self.__get_os_info()
        ## short name  + major version 
        return self.shortname() + self.m['Release'].split('.')[0]

    def osname(self):
        if not self.m:
            self.__get_os_info()
        return self.m['Description']

    def setup_env(self, target_arch):
        pass
        
    def cmake_bin(self, cwd="."):
        re, c = runcmd('which cmake')
        if re == 0:
            return c.strip()
        else:
            CMAKE_BIN_ =  os.path.join(cwd, r'tools\cmake_linux\bin\cmake')
            runcmd("chmod +x " + CMAKE_BIN_)
            return CMAKE_BIN_

    def doxgen_bin(self):
        return "doxgen"

    def swig_bin(self):
        return "swig"

    def make_bin(self):
        return 'make'

def clear_cache(x):
    import shutil
    #shutil.rmtree(x)
    for f in os.listdir(x):
        if path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

if __name__=="__main__": 
    if os.name == 'posix':
        a=xm_linux_env()
        print a.shortname()
        print a.cmake_bin()
        print a.is_x64()
        print a.shortosname()
    else:
        a = xm_win_env()
        print a.shortname()
        print a.cmake_bin()
        print a.is_x64()
        print a.shortosname()
    
