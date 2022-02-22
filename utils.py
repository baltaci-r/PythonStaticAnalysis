import graphviz as gv
import re
import ast
import numbers
from uuid import uuid4 as uuid
from graphviz import Source, Digraph


# AST utils:
# __________

class GraphRenderer:
    graphattrs = {
        'labelloc': 't',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'margin': '0',
    }

    nodeattrs = {
        'color': 'white',
        'fontcolor': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    }

    edgeattrs = {
        'color': 'white',
        'fontcolor': 'white',
    }

    _graph = None
    _rendered_nodes = None


    @staticmethod
    def _escape_dot_label(str):
        return str.replace("\\", "\\\\").replace("|", "\\|").replace("<", "\\<").replace(">", "\\>")


    def _render_node(self, node):
        if isinstance(node, (str, numbers.Number)) or node is None:
            node_id = uuid()
        else:
            node_id = id(node)
        node_id = str(node_id)

        if node_id not in self._rendered_nodes:
            self._rendered_nodes.add(node_id)
            # why are we checking if node is list or dict?
            if isinstance(node, dict):
                self._render_dict(node, node_id)
            elif isinstance(node, list):
                self._render_list(node, node_id)
            else:
                self._graph.node(node_id, label=self._escape_dot_label(str(node)))

        return node_id


    def _render_dict(self, node, node_id):
        self._graph.node(node_id, label=node.get("node_type", "[dict]"))
        for key, value in node.items():
            if key == "node_type":
                continue
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(key))


    def _render_list(self, node, node_id):
        self._graph.node(node_id, label="[list]")
        for idx, value in enumerate(node):
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(str(idx)))


    def render(self, data, outname='Digraph', *, label=None):

        # create the graph
        graphattrs = self.graphattrs.copy()
        if label is not None:
            graphattrs['label'] = self._escape_dot_label(label)
        graph = gv.Digraph(filename=outname, graph_attr = graphattrs, node_attr = self.nodeattrs, edge_attr = self.edgeattrs)

        # recursively draw all the nodes and edges
        self._graph = graph
        self._rendered_nodes = set()
        self._render_node(data)
        self._graph = None
        self._rendered_nodes = None

        # display the graph
        # graph.format = "png"
        # graph.view()
        # subprocess.Popen(['xdg-open', "test.pdf"])


        return graph


def to_camelcase(string):
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


# CFG utils:
# ----------

def unhack(v):
    for i in ['if', 'while', 'for', 'elif']:
        v = re.sub(r'^_%s:' % i, '%s:' % i, v)
    return v


def to_graph(cache, outname='Digraph', arcs=[]):
    graph = Digraph(filename=outname)
    colors = {0: 'blue', 1: 'red'}
    kind = {0: 'T', 1: 'F'}
    cov_lines = set(i for i, j in arcs)
    for nid, cnode in cache.items():
        lineno = cnode.lineno()
        shape, peripheries = 'oval', '1'
        if isinstance(cnode.ast_node, ast.AnnAssign):
            if cnode.ast_node.target.id in {'_if', '_for', '_while'}:
                shape = 'diamond'
            elif cnode.ast_node.target.id in {'enter', 'exit'}:
                shape, peripheries = 'oval', '2'
        else:
            shape = 'rectangle'
        graph.node(cnode.i(), "%d: %s" % (lineno, unhack(cnode.source())),
                   shape=shape, peripheries=peripheries)
        for pn in cnode.parents:
            plineno = pn.lineno()
            if hasattr(pn, 'calllink') and pn.calllink > 0 and not hasattr(cnode, 'calleelink'):
                graph.edge(pn.i(), cnode.i(), style='dotted') #, weight=100)
                continue

            if arcs:
                if (plineno, lineno) in arcs:
                    graph.edge(pn.i(), cnode.i(), color='green')
                elif plineno == lineno and lineno in cov_lines:
                    graph.edge(pn.i(), cnode.i(), color='green')
                # child is exit and parent is covered
                elif hasattr(cnode, 'fn_exit_node') and plineno in cov_lines:
                    graph.edge(pn.i(), cnode.i(), color='green')
                # parent is exit and one of its parents is covered.
                elif hasattr(pn, 'fn_exit_node') and len(
                        set(n.lineno() for n in pn.parents) | cov_lines) > 0:
                    graph.edge(pn.i(), cnode.i(), color='green')
                # child is a callee (has calleelink) and one of the parents is covered.
                elif plineno in cov_lines and hasattr(cnode, 'calleelink'):
                    graph.edge(pn.i(), cnode.i(), color='green')
                else:
                    graph.edge(pn.i(), cnode.i(), color='red')
            else:
                order = {c.i(): i for i, c in enumerate(pn.children)}
                if len(order) < 2:
                    graph.edge(pn.i(), cnode.i())
                else:
                    o = order[cnode.i()]
                    graph.edge(pn.i(), cnode.i(), color=colors[o], label=kind[o])
    return graph