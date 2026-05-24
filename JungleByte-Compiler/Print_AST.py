# ===== AST BUILDERS =====
# Job: create abstract syntax tree nodes 

def Program(funcs):
    return ("PROGRAM", funcs)

def Function(name, params, ret, body):
    return ("FUNCTION", name, params, ret, body)

def Block(stmts):
    return ("BLOCK", stmts)

def Assign(name, expr):
    return ("ASSIGN", name, expr)

def Call(name, args):
    return ("CALL", name, args)

def Print(expr):
    return ("PRINT", expr)

def Return(expr):
    return ("RETURN", expr)

# Job: represent IF with (branches, else_block)
def If(branches, else_block):
    return ("IF", branches, else_block)

def While(cond, body):
    return ("WHILE", cond, body)

def For(var, limit, body):
    return ("FOR", var, limit, body)

def Break():
    return ("BREAK",)

def Continue():
    return ("CONTINUE",)

# Job: represent binary operation
def BinOp(op, left, right):
    return ("BIN_OP", op, left, right)


# ===== TREE PRINTER =====
# Job: display AST in readable tree form

def print_tree(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "

    # Job: handle AST node
    if isinstance(node, tuple):
        node_type = node[0]
        print(prefix + connector + node_type)

        # Job: special formatting for IF
        if node_type == "IF":

            branches = node[1]
            else_block = node[2]

            new_prefix = prefix + (
                "    " if is_last else "│   "
            )

            for i, (cond, block) in enumerate(branches):

                # CONDITION
                print_tree(
                    cond,
                    new_prefix,
                    False
                )

                # BODY
                print_tree(
                    block,
                    new_prefix,
                    True
                )

            # ELSE
            if else_block:

                print(
                    new_prefix + "└── ELSE"
                )

                print_tree(
                    else_block,
                    new_prefix + "    ",
                    True
                )

            return

        # Job: print children nodes
        children = node[1:]
        for i, child in enumerate(children):
            last = (i == len(children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(child, new_prefix, last)

    # Job: handle list of nodes
    elif isinstance(node, list):
        for i, item in enumerate(node):
            last = (i == len(node) - 1)
            print_tree(item, prefix, last)

    # Job: print leaf value
    else:
        print(prefix + connector + str(node))