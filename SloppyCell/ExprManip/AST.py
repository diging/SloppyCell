from ast import *

TINY = 1e-12

# def _node_equal(self, other):
#     """
#     Return whether self and other represent the same expressions.
#     Unfortunately, the Node class in Python 2.3 doesn't define ==, so
#     we need to write our own.
#     """
#     # We're not equal if other isn't a Node, or if other is a different class.
#     if not isinstance(other, Node) or not isinstance(other, self.__class__):
#         return False
#     # Loop through all children, checking whether they are equal
#     for self_child, other_child in zip(self.getChildren(), other.getChildren()):
#         if not self_child == other_child:
#             return False
#     # If we get here, our two nodes much be equal
#     return True
# Node = AST
# Node.__eq__ = _node_equal
 
def strip_parse(expr):
    """
    Return an abstract syntax tree (AST) for an expression.

    This removes the enclosing cruft from a call to compiler.parse(expr)
    """
    # The .strip() ignores leading and trailing whitespace, which would 
    #  otherwise give syntax errors.
    tree = parse(str(expr).strip())
    print("ffffffffffffffffffffffffffffffffffffffffffffffffffffff", dump(tree))
    return  tree.body[0].value

# This defines the order of operations for the various node types, to determine
#  whether or not parentheses are necessary.
_OP_ORDER = {Name: 0,
            Constant: 0,
             Call: 0,
             Subscript: 0,
             Slice: 0,
             Slice: 0,
             BinOp: 0,
             UnaryOp: 0,
             Pow: 3,
             USub: 4,
             UAdd: 4,
             Mult: 5,
             Div: 5,
             Sub: 10,
             Add: 10,
             Compare: 11,
             Not: 11,
             And: 11,
             Or: 11,
             Expr: 100
            }

# This is just an instance of Discard to use for the default
_FARTHEST_OUT = Expr(None)

# These are the attributes of each node type that are other nodes.
_node_attrs = {Name: (),
               Add: (),
               Sub: (),
               Mult: (),
               Div: (),
               Call: ('args', 'keywords'),
               Pow: (),
               USub: (),
               UAdd: (),
               Slice: ('lower', 'upper'),
               Slice: ('nodes',),
               Subscript: ('subs',),
               Subscript: ('value', 'slice', 'ctx',),
               Compare: ('left', 'ops', 'comparators'),
               Not: (),
               Or: (),
               And: (),
               BoolOp: ('op', 'values'),
               UnaryOp: ('op', 'operand'),
               BinOp: ('left', 'op', 'right'),
               }

def ast2str(ast):
    """
    Return the string representation of an AST.
    """
    return unparse(ast)
 
def ast2str(node, outer = _FARTHEST_OUT , adjust = 0):
    """
    Return the string representation of an AST.
    outer: The AST's 'parent' node, used to determine whether or not to 
        enclose the result in parentheses. The default of _FARTHEST_OUT will
        never enclose the result in parentheses.
    adjust: A numerical value to adjust the priority of this ast for
        particular cases. For example, the denominator of a '/' needs 
        parentheses in more cases than does the numerator.
    """
    return unparse(node)
    if isinstance(node, Name):
        out = node.name
    elif isinstance(node, Constant):
        out = str(node.value)
    elif isinstance(node, Add):
        out = '%s + %s' % (ast2str(node.left, node),
                           ast2str(node.right, node))
    elif isinstance(node, Sub):
        out = '%s - %s' % (ast2str(node.left, node),
                           ast2str(node.right, node, adjust = TINY))
    elif isinstance(node, Mult):
        out = '%s*%s' % (ast2str(node.left, node),
                           ast2str(node.right, node))
    elif isinstance(node, Div):
        # The adjust ensures proper parentheses for x/(y*z)
        out = '%s/%s' % (ast2str(node.left, node),
                           ast2str(node.right, node, adjust = TINY))
    elif isinstance(node, Pow):
        # The adjust ensures proper parentheses for (x**y)**z
        out = '%s**%s' % (ast2str(node.left, node, adjust = TINY),
                          ast2str(node.right, node))
    elif isinstance(node, USub):
        out = '-%s' % ast2str(node.expr, node)
    elif isinstance(node, UAdd):
        out = '+%s' % ast2str(node.expr, node)
    elif isinstance(node, Call):
        args = [ast2str(arg) for arg in node.args]
        out = '%s(%s)' % (ast2str(node.node), ', '.join(args))
    elif isinstance(node, Subscript):
        subs = [ast2str(sub) for sub in node.subs]
        out = '%s[%s]' % (ast2str(node.expr), ', '.join(subs))
    elif isinstance(node, Slice):
        out = '%s[%s:%s]' % (ast2str(node.expr), ast2str(node.lower), 
                             ast2str(node.upper))
    elif isinstance(node, Slice):
        nodes = [ast2str(node) for node in node.nodes]
        out = ':'.join(nodes)
    elif isinstance(node, Compare):
        expr = ast2str(node.expr, node, adjust=6+TINY)
        out_l = [expr]
        for op, val in node.ops:
            out_l.append(op)
            out_l.append(ast2str(val, node, adjust=6+TINY))
        out = ' '.join(out_l)
    elif isinstance(node, And):
        nodes = [ast2str(node, node, adjust=TINY) for node in node.nodes]
        out = ' and '.join(nodes)
    elif isinstance(node, Or):
        nodes = [ast2str(node, node, adjust=TINY) for node in node.nodes]
        out = ' or '.join(nodes)
    elif isinstance(node, Not):
        out = 'not %s' % ast2str(node.expr, node, adjust=TINY)
    # Ensure parentheses by checking the _OP_ORDER of the outer and inner ASTs
    if _need_parens(outer, node, adjust):
        return out
    else:
        return '(%s)' % out
   

def _need_parens(outer, inner, adjust):
    """
    Return whether or not the inner AST needs parentheses when enclosed by the
    outer.

    adjust: A numerical value to adjust the priority of this ast for
        particular cases. For example, the denominator of a '/' needs 
        parentheses in more cases than does the numerator.
    """
    print(outer, inner, adjust)
    return _OP_ORDER[outer.__class__] >= _OP_ORDER[inner.__class__] + adjust

def _collect_num_denom(ast, nums, denoms):
    """
    Append to nums and denoms, respectively, the nodes in the numerator and 
    denominator of an AST.
    """
    if not (isinstance(ast, BinOp) and  (isinstance(ast.op, Mult) or isinstance(ast.op, Div))):
        nums.append(ast)
        print("exit", nums, denoms)
        return
    
    if isinstance(ast.left, BinOp) and (isinstance(ast.left.op, Div) or isinstance(ast.left.op, Mult)):
        # print("lefttttttttttttttttttttttt dumppppppppp", dump(ast.left))
        # print("left", nums, denoms)
        _collect_num_denom(ast.left, nums, denoms)
        # print("leftttttttttttttttttttttttt", nums, denoms)
    else:
        # print("left else condition", nums, denoms)
        nums.append(ast.left)
        # print("left else conditionnnnnnnnnnnnnnnnnnnnnnnnnnn", dump(nums[0]), denoms)
    print("excxxxxxxxxxxxxxxx", dump(ast.right))
    if isinstance(ast.right, BinOp) and (isinstance(ast.right.op, Div) or isinstance(ast.right.op, Mult)):
        # print("ffffffffffffffffffff", dump(ast.right))
        if isinstance(ast.op, Div):
            # print("right if condition div", nums, denoms)
            _collect_num_denom(ast.right, denoms, nums)
            # print("right if condition divvvvvvvvvvvvvvvvvvvvvvvvv", nums, denoms)
        elif isinstance(ast.op, Mult):
            print("right if condition mult", nums, denoms)
            _collect_num_denom(ast.right, nums, denoms)
            # print("right if condition multttttttttttttttttttttttttttttttt", nums, denoms)
    else:
        if isinstance(ast.op, Div):
            # print("final else", nums, denoms)
            denoms.append(ast.right)
            # print("final elseeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", nums, denoms)
        elif isinstance(ast.op, Mult):
            # print("here else Nulttttttttttttttttttttttttttt", nums, denoms)
            nums.append(ast.right)
            # print("here else xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", nums, denoms)
    

def _collect_pos_neg(ast, poss, negs):
    """
    Append to poss and negs, respectively, the nodes in AST with positive and 
    negative factors from a addition/subtraction chain.
    """
    # 
    # This code is almost duplicated from _collect_num_denom. 
    # The additional twist is handling UnarySubs.
    #
    
    if not ((isinstance(ast, BinOp) and  (isinstance(ast.op, Sub) or isinstance(ast.op, Add))) or (isinstance(ast, UnaryOp) and (isinstance(ast.op,USub) or isinstance(ast.op, UAdd) ))):
        poss.append(ast)
        return
    if (isinstance(ast.op, Sub) or isinstance(ast.op, Add)) and isinstance(ast, BinOp):
        if isinstance(ast.left, BinOp) and (isinstance(ast.left.op, Add) or isinstance(ast.left.op, Sub)):
            _collect_pos_neg(ast.left, poss, negs)
        elif isinstance(ast.left, UnaryOp):
            _collect_pos_neg(ast.left, poss, negs) 
        else:
            poss.append(ast.left)
            
        if isinstance(ast.right, BinOp) and (isinstance(ast.right.op, Add) or isinstance(ast.right.op, Sub)):
            if isinstance(ast.op, Add):
                _collect_pos_neg(ast.right, poss, negs)
            elif isinstance(ast.op, Sub):
                _collect_pos_neg(ast.right, negs, poss)
        elif isinstance(ast.right, UnaryOp):
             _collect_pos_neg(ast.right, negs, poss)      
        else:
            if isinstance(ast.op, Add):
                poss.append(ast.right)
            elif isinstance(ast.op, Sub):
                negs.append(ast.right)
                
    if isinstance(ast, UnaryOp) and (isinstance(ast.op, USub) or isinstance(ast.op, UAdd)):
        if isinstance(ast.operand, Constant) or isinstance(ast.operand, Name):
            if isinstance(ast.op, USub):
                negs.append(ast.operand)
            if isinstance(ast.op, UAdd):
                poss.append(ast.operand)
            return
        else:
            _collect_pos_neg(ast.operand, poss, negs)


def _make_product(terms):
    """
    Return an AST expressing the product of all the terms.
    """
    if terms:
        product = terms[0]
        for term in terms[1:]:
            product = BinOp(left=product, op=Mult(), right=term)
            # product = Mult((product, term))
        return product 
    else:
        return Constant(value=1)


def recurse_down_tree(ast, func, args=()):
    print("start",  ast)
    if isinstance(ast, list):
        for ii, elem in enumerate(ast):
            ast[ii] = func(elem, *args)
    elif isinstance(ast, tuple):
        ast = tuple(func(list(ast), *args))
    elif ast.__class__ in _node_attrs:
        # print("class", ast.args)
        print("a", _node_attrs[ast.__class__])
        for attr_name in _node_attrs[ast.__class__]:
            print("attr name", attr_name)
            attr = getattr(ast, attr_name)
            # print("attr", attr)
            # print("*argsssssss", *args)
            attr_mod = func(attr, *args)
            # print("after", attr_mod)
            # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            # print(attr)
            # print(attr_mod)
            setattr(ast, attr_name, attr_mod)

    return ast
