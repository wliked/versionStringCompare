import sys,_winreg,os
import re
import subprocess
import shlex
import copy

path = os.path

_XMODULE_CURRENT_VC_VERSION="8.0"     # Now, we are using VS2005 as compiler.
#cwd = path.dirname(sys.argv[0])
#_XMODULE_CMAKE_BIN_DIR=path.join(cwd, r'tools\cmake_win\bin')

## Common ---------------------------------------------------------------------

def debug(s): 
    sys.stdout.write(s+"\n")

class VisualCException(Exception):
    pass
class UnsupportedVersion(VisualCException):
    pass
class MissingConfiguration(VisualCException):
    pass

class BatchFileExecutionError(VisualCException):
    pass
def normalize_env(env, keys, force=False):
    """Given a dictionary representing a shell environment, add the variables
    from os.environ needed for the processing of .bat files; the keys are
    controlled by the keys argument.

    It also makes sure the environment values are correctly encoded.

    If force=True, then all of the key values that exist are copied
    into the returned dictionary.  If force=false, values are only
    copied if the key does not already exist in the copied dictionary.

    Note: the environment is copied."""
    normenv = {}
    if env:
        for k in env.keys():
            normenv[k] = copy.deepcopy(env[k]).encode('mbcs')

        for k in keys:
            if k in os.environ and (force or not k in normenv):
                normenv[k] = os.environ[k].encode('mbcs')

    return normenv

def get_output(vcbat, args = None, env = None):
    """Parse the output of given bat file, with given args."""
    
    if env is None:
        # Create a blank environment, for use in launching the tools
        env = {}
        env['ENV'] = os.environ

    # TODO:  This is a hard-coded list of the variables that (may) need
    # to be imported from os.environ[] for v[sc]*vars*.bat file
    # execution to work.  This list should really be either directly
    # controlled by vc.py, or else derived from the common_tools_var
    # settings in vs.py.
    vars = [
        'COMSPEC',
        'VS90COMNTOOLS',
        'VS80COMNTOOLS',
        'VS71COMNTOOLS',
        'VS70COMNTOOLS',
        'VS60COMNTOOLS',
    ]
    env['ENV'] = normalize_env(env['ENV'], vars, force=False)

    if args:
        debug("Calling '%s %s'" % (vcbat, args))
        
        popen = subprocess.Popen('"%s" %s & set' % (vcbat, args), stdin=None,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE,
                             shell  = True)
        
    else:
        debug("Calling '%s'" % vcbat)
        popen = subprocess.Popen( '"%s" & set' % vcbat,
                                  stdin = None,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell = True)

    # Use the .stdout and .stderr attributes directly because the
    # .communicate() method uses the threading module on Windows
    # and won't work under Pythons not built with threading.
    stdout = popen.stdout.read()
    stderr = popen.stderr.read()
    if stderr:
        # TODO: find something better to do with stderr;
        # this at least prevents errors from getting swallowed.
        import sys
        sys.stderr.write(stderr)
    if popen.wait() != 0:
        raise IOError(stderr.decode("mbcs"))

    output = stdout.decode("mbcs")
    return output

def parse_output(output, keep = ("INCLUDE", "LIB", "LIBPATH", "PATH")):
    # dkeep is a dict associating key: path_list, where key is one item from
    # keep, and pat_list the associated list of paths

    dkeep = dict([(i, []) for i in keep])

    # rdk will  keep the regex to match the .bat file output line starts
    rdk = {}
    for i in keep:
        rdk[i] = re.compile('%s=(.*)' % i, re.I)

    def add_env(rmatch, key, dkeep=dkeep):
        plist = rmatch.group(1).split(os.pathsep)
        for p in plist:
            # Do not add empty paths (when a var ends with ;)
            if p:
                p = p.encode('mbcs')
                # XXX: For some reason, VC98 .bat file adds "" around the PATH
                # values, and it screws up the environment later, so we strip
                # it. 
                p = p.strip('"')
                dkeep[key].append(p)

    for line in output.splitlines():
        for k,v in rdk.items():
            m = v.match(line)
            if m:
                add_env(m, k)

    return dkeep


_is_win64 = None

def is_win64():
    """Return true if running on windows 64 bits.
    
    Works whether python itself runs in 64 bits or 32 bits."""
    # Unfortunately, python does not provide a useful way to determine
    # if the underlying Windows OS is 32-bit or 64-bit.  Worse, whether
    # the Python itself is 32-bit or 64-bit affects what it returns,
    # so nothing in sys.* or os.* help.  

    # Apparently the best solution is to use env vars that Windows
    # sets.  If PROCESSOR_ARCHITECTURE is not x86, then the python
    # process is running in 64 bit mode (on a 64-bit OS, 64-bit
    # hardware, obviously).
    # If this python is 32-bit but the OS is 64, Windows will set
    # ProgramW6432 and PROCESSOR_ARCHITEW6432 to non-null.
    # (Checking for HKLM\Software\Wow6432Node in the registry doesn't
    # work, because some 32-bit installers create it.)
    global _is_win64
    if _is_win64 is None:
        # I structured these tests to make it easy to add new ones or
        # add exceptions in the future, because this is a bit fragile.
        _is_win64 = False
        if os.environ.get('PROCESSOR_ARCHITECTURE','x86') != 'x86':
            _is_win64 = True
        if os.environ.get('PROCESSOR_ARCHITEW6432'):
            _is_win64 = True
        if os.environ.get('ProgramW6432'):
            _is_win64 = True
    return _is_win64

def RegGetValue(root, key):
        """This utility function returns a value in the registry
        without having to open the key first.  Only available on
        Windows platforms with a version of Python that can read the
        registry.  

        """
        RegOpenKeyEx    = _winreg.OpenKeyEx
        RegEnumKey      = _winreg.EnumKey
        RegEnumValue    = _winreg.EnumValue
        RegQueryValueEx = _winreg.QueryValueEx
        RegError        = _winreg.error
        # I would use os.path.split here, but it's not a filesystem
        # path...
        p = key.rfind('\\') + 1
        keyp = key[:p-1]          # -1 to omit trailing slash
        val = key[p:]
        k = RegOpenKeyEx(root, keyp)
        return RegQueryValueEx(k,val)

def set_winddk_env(target_arch):

    ddkdir = 'C:\\WINDDK\\3790.1830'	
    if os.path.exists(ddkdir):
        ddkdir.replace('\\', '\\\\')
        inc = ddkdir + '\\inc\\ddk\\wnet'
        os.environ['INCLUDE'] = inc

        cpu = 'i386'
        if 'x64' == target_arch:
           cpu = 'amd64'

        lib = ddkdir + '\\lib\\wnet\\' + cpu
        os.environ['LIB'] = lib

    else:
        error_msg = 'Can not find WINDDK in path `c:\\WINDDK\\3790.1830`'
        debug(error_msg) 
        raise MissingConfiguration(error_msg)


## Common func ---------------------------->8--------------------------

_VCVER_TO_PRODUCT_DIR = {
        '10.0': [
            r'Microsoft\VisualStudio\10.0\Setup\VC\ProductDir'],
        '9.0': [
            r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir'],
        '8.0': [
            r'Microsoft\VisualStudio\8.0\Setup\VC\ProductDir'],
}


def find_vc_pdir(msvc_version):
    """Try to find the product directory for the given
    version.

    Note
    ----
    If for some reason the requested version could not be found, an
    exception which inherits from VisualCException will be raised."""
    root = 'Software\\'
    if is_win64():
        root = root + 'Wow6432Node\\'
    try:
        hkeys = _VCVER_TO_PRODUCT_DIR[msvc_version]

    except KeyError:
        raise UnsupportedVersion("Unknown version %s" % msvc_version)

    for key in hkeys:
        key = root + key
        try:
            comps = RegGetValue(_winreg.HKEY_LOCAL_MACHINE,key)
        except WindowsError, e:
            debug('find_vc_dir(): no VC registry key %s' % repr(key))
        else:
            if os.path.exists(comps[0]):
                return comps[0]
            else:
                debug('find_vc_dir(): reg says dir is %s, but it does not exist. (ignoring)'\
                          % comps[0])
                raise MissingConfiguration("registry dir %s not found on the filesystem" % comps[0])
    return None

from string import digits as string_digits
def find_batch_file(msvc_version):
    """
    Find the location of the batch script which should set up the compiler
    for any TARGET_ARCH whose compilers were installed by Visual Studio/VCExpress
    """
    pdir = find_vc_pdir(msvc_version)
    if pdir is None:
        raise NoVersionFound("No version of Visual Studio found")
        
    debug('vc.py: find_batch_file() pdir:%s'%pdir)

    # filter out e.g. "Exp" from the version name
    msvc_ver_numeric = ''.join([x for x in msvc_version if x in string_digits + "."])
    vernum = float(msvc_ver_numeric)
    if 7 <= vernum < 8:
        pdir = os.path.join(pdir, os.pardir, "Common7", "Tools")
        batfilename = os.path.join(pdir, "vsvars32.bat")
    elif vernum < 7:
        pdir = os.path.join(pdir, "Bin")
        batfilename = os.path.join(pdir, "vcvars32.bat")
    else: # >= 8
        batfilename = os.path.join(pdir, "vcvarsall.bat")

    if not os.path.exists(batfilename):
        debug("Not found: %s" % batfilename)
        batfilename = None
    
    return batfilename

def script_env(script, args=None):
    stdout = get_output(script, args)
    # Stupid batch files do not set return code: we take a look at the
    # beginning of the output for an error message instead
    olines = stdout.splitlines()
    if olines[0].startswith("The specified configuration type is missing"):
        raise BatchFileExecutionError("\n".join(olines[:2]))

    return parse_output(stdout)

def choose_batch_param(taget_type):
    if not is_win64():
        if taget_type in ['x86', 'X86']:
            return 'x86'
        elif taget_type in ['x64','amd64', 'x86_amd64']:
            return 'x86_amd64'
    else:
        if taget_type in ['x86']:
            return 'x86'
        elif taget_type in ['x64', 'amd64']:
            return 'x64'


def setup_env(target_arch):
    ## set winddk env
    set_winddk_env(target_arch);
    ## set environment of VC compiler
    batchfile = find_batch_file(_XMODULE_CURRENT_VC_VERSION) 
    env = script_env(batchfile, choose_batch_param(target_arch))
    
    for k in env.keys():
        os.environ[k] = ';'.join(env[k])

__cwd = os.path.dirname(sys.argv[0])
#CMAKE_BIN_ =  os.path.join(__cwd, r'tools\cmake_win\bin\cmake.exe')
#if not os.path.exists(CMAKE_BIN_):
#    raise "CMake is not exited"

def clear_cache(x):
    import shutil
    #shutil.rmtree(x)
    for f in os.listdir(x):
        if path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)
