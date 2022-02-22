from graphs import PyAST, PyCFG, PyCG
import os

class GraphGenerator:
    def __init__(self, code, outname='Digraph', format='png'):
        self.code = code
        self.format = format
        self.outname = os.path.join('output',outname)
        self.makeOutDir()

    def makeOutDir(self):
        if not os.path.exists('output'):
            os.mkdir('output')

    def genAST(self):
        ast = PyAST()
        g=ast.generate(self.code, self.outname)
        g.format=self.format
        g.view()

    def genCFG(self):
        cfg=PyCFG()
        g=cfg.generate(self.code, self.outname)
        g.format = self.format
        g.view()

    def genCG(self):
        cf = PyCG()
        g = cf.generate(self.code, self.outname)
        g.format = self.format
        g.view()