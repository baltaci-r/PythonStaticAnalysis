import os
import shutil
from graphviz import Source
import tempfile
import subprocess

########
PYAN = 'pyan3' if shutil.which('pyan3') is not None else 'pyan'

if shutil.which(PYAN) is None:
    # If installed from pypi, pyan may still be missing
    os.system('pip install "git+https://github.com/uds-se/pyan#egg=pyan"')
    PYAN = 'pyan3' if shutil.which('pyan3') is not None else 'pyan'

assert shutil.which(PYAN) is not None


class PyCF:
    def __init__(self):
        pass

    def generate(self, code, outname='Digraph'):
        with tempfile.NamedTemporaryFile(mode='w') as tmp:
            tmp.write(code)

            p = subprocess.Popen(f'{PYAN} {tmp.name} --uses --defines --colored --grouped --annotated --dot > {outname}.dot', shell=True) #> {label}.dot'])
            p.wait()
            g = Source.from_file(f'{outname}.dot')
        return g