import ast
from utils import *

class PyAST:

    def __init__(self):
        None


    def transform_ast(self, code):
        if isinstance(code, ast.AST):
            node = {to_camelcase(k): self.transform_ast(getattr(code, k)) for k in code._fields}
            node['node_type'] = to_camelcase(code.__class__.__name__)
            return node
        elif isinstance(code, list):
            return [self.transform_ast(el) for el in code]
        else:
            return code


    def generate(self, code, outname='Digraph'):
        tree = ast.parse(code)
        transformed_ast = self.transform_ast(tree)
        renderer = GraphRenderer()
        return renderer.render(transformed_ast, outname)
