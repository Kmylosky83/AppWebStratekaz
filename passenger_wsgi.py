import sys, os
INTERP = os.path.join(os.environ['HOME'], 'venv', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
    
from run import app as application