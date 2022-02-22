import argparse
from genGraph import GraphGenerator

def generateGraph(args):
    graphType = args.t
    filePath = args.p

    assert args.p or args.s
    if args.p and args.s:
        raise ValueError('Please specify either a filepath or a code string')
    if args.p:
        if filePath[-3:]!='.py':
            raise ValueError('This analysis tool accepts python files only,\nfor java please check ###\n for COBOL please check ###')
    if args.p:
        source = open(filePath, "r")
        code = source.read()
    elif args.s:
        code = args.s

    generator= GraphGenerator(code, args.f, args.o)
    if graphType =='ast':
        generator.genAST()
    elif graphType == 'cfg':
        generator.genCFG()
    elif graphType == 'cf':
        generator.genCF()
    elif graphType == 'all':
        generator.genAST()
        generator.genCFG()
        generator.genCF()


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', default='ast', choices=['ast', 'cfg', 'cf', 'all'], help='Type of static analysis')
    parser.add_argument('-p', type=str, help='Filepath for python code')
    parser.add_argument('-s', help='Use to pass python file as a string')
    parser.add_argument('-f', default='graph', help='Filename for output')
    parser.add_argument('-o', default='png', help='Output format')
    args = parser.parse_args()

    generateGraph(args)

