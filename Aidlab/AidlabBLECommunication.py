import sys
if 'linux' in sys.platform:
    from .linux import *
elif 'darwin' in sys.platform:
    from .mac import *
else:
    raise RuntimeError("Unsupported operating system: {}".format(sys.platform))
