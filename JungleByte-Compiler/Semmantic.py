# ===== SEMANTIC ERROR =====
# Job: define custom error for semantic phase

class SemanticError(Exception):
    pass


# =========================================================
# SEMANTIC ANALYZER
# =========================================================
# Job: perform scope, type, and function validation

class Semantic:

    def __init__(self):

        # Job: stack of variable scopes
        self.scopes = [{}]

        # Job: functions table
        # name -> (params, return_type)
        self.functions = {}

        # Job: current function return type
        self.current_return = None

        # Job: detect return existence
        self.has_return = False

        # Job: track loop nesting
        self.in_loop = 0


# =========================================================
# SCOPE HANDLING
# =========================================================

    # Job: enter new scope
    def enter_scope(self):
        self.scopes.append({})

    # Job: exit current scope
    def exit_scope(self):
        self.scopes.pop()

    # Job: define variable
    def define(self, name, typ):
        self.scopes[-1][name] = typ

    # Job: lookup variable in scopes
    def lookup(self, name):

        for scope in reversed(self.scopes):

            if name in scope:
                return scope[name]

        return None


# =========================================================
# ENTRY POINT
# =========================================================

    # Job: start semantic analysis
    def analyze(self, ast):

        _, items = ast

        # ===== SPLIT =====
        functions = [
            i for i in items
            if i[0] == "FUNCTION"
        ]

        statements = [
            i for i in items
            if i[0] != "FUNCTION"
        ]

        # ===== REGISTER FUNCTIONS =====
        for f in functions:

            _, name, params, ret, _ = f

            self.functions[name] = (
                params,
                ret
            )

        # ===== ANALYZE FUNCTIONS =====
        for f in functions:
            self.visit_function(f)

        # ===== ANALYZE GLOBALS =====
        for stmt in statements:
            self.visit(stmt)


# =========================================================
# FUNCTION
# =========================================================

    # Job: analyze function
    def visit_function(self, node):

        _, name, params, ret, body = node

        self.enter_scope()

        self.current_return = ret

        self.has_return = False

        # ===== DEFINE PARAMS =====
        for p in params:
            self.define(p, "int")

        self.visit_block(body)

        # ===== RETURN RULE =====
        if (
            name != "main"
            and ret != "void"
            and not self.has_return
        ):

            raise SemanticError(
                f"{name} must return a value"
            )

        self.exit_scope()


# =========================================================
# BLOCK
# =========================================================

    # Job: process statements
    def visit_block(self, node):

        for stmt in node[1]:
            self.visit(stmt)


# =========================================================
# STATEMENTS
# =========================================================

    # Job: analyze statement
    def visit(self, node):

        t = node[0]

        # =================================================
        # ASSIGN
        # =================================================

        if t == "ASSIGN":

            _, name, expr = node

            typ = self.eval_expr(expr)

            self.define(name, typ)

        # =================================================
        # PRINT
        # =================================================

        elif t == "PRINT":

            self.eval_expr(node[1])

        # =================================================
        # FUNCTION CALL
        # =================================================

        elif t == "CALL":

            _, name, args = node

            if name not in self.functions:

                raise SemanticError(
                    f"{name} not defined"
                )

            params, _ = self.functions[name]

            if len(args) != len(params):

                raise SemanticError(
                    f"{name} expects "
                    f"{len(params)} args, "
                    f"got {len(args)}"
                )

            for a in args:
                self.eval_expr(a)

        # =================================================
        # RETURN
        # =================================================

        elif t == "RETURN":

            if self.current_return == "void":

                raise SemanticError(
                    "void function should not return value"
                )

            value_type = self.eval_expr(node[1])

            if value_type != self.current_return:

                raise SemanticError(
                    f"expected return type "
                    f"{self.current_return}, "
                    f"got {value_type}"
                )

            self.has_return = True

        # =================================================
        # IF
        # =================================================

        elif t == "IF":

            cases, else_block = node[1], node[2]

            for cond, block in cases:

                self.eval_expr(cond)

                self.visit_block(block)

            if else_block:
                self.visit_block(else_block)

        # =================================================
        # WHILE
        # =================================================

        elif t == "WHILE":

            self.in_loop += 1

            self.eval_expr(node[1])

            self.visit_block(node[2])

            self.in_loop -= 1

        # =================================================
        # FOR
        # =================================================

        elif t == "FOR":

            self.in_loop += 1

            self.enter_scope()

            self.define(node[1], "int")

            self.eval_expr(node[2])

            self.visit_block(node[3])

            self.exit_scope()

            self.in_loop -= 1

        # =================================================
        # CONTINUE
        # =================================================

        elif t == "CONTINUE":

            if self.in_loop == 0:

                raise SemanticError(
                    "continue outside loop"
                )

        # =================================================
        # BREAK
        # =================================================

        elif t == "BREAK":

            if self.in_loop == 0:

                raise SemanticError(
                    "break outside loop"
                )


# =========================================================
# EXPRESSIONS
# =========================================================

    # Job: evaluate expression type
    def eval_expr(self, expr):

        # =================================================
        # LITERAL / VARIABLE
        # =================================================

        if isinstance(expr, str):

            # ===== STRING =====
            if (
                expr.startswith('"')
                and expr.endswith('"')
            ):
                return "string"

            # ===== INTEGER =====
            if expr.isdigit():
                return "int"

            # ===== FLOAT =====
            try:

                float(expr)

                if "." in expr:
                    return "float"

            except:
                pass

            # ===== VARIABLE =====
            typ = self.lookup(expr)

            if typ is None:

                raise SemanticError(
                    f"{expr} not defined"
                )

            return typ

        # =================================================
        # FUNCTION CALL
        # =================================================

        if expr[0] == "CALL":

            _, name, args = expr

            # ===== EXISTS =====
            if name not in self.functions:

                raise SemanticError(
                    f"{name} not defined"
                )

            # ===== FUNCTION INFO =====
            params, ret_type = self.functions[name]

            # ===== ARG COUNT =====
            if len(args) != len(params):

                raise SemanticError(
                    f"{name} expects "
                    f"{len(params)} args, "
                    f"got {len(args)}"
                )

            # ===== VALIDATE ARGS =====
            for a in args:
                self.eval_expr(a)

            return ret_type

        # =================================================
        # BINARY OP
        # =================================================

        if expr[0] == "BIN_OP":

            _, op, left, right = expr

            l = self.eval_expr(left)

            r = self.eval_expr(right)

            # ===== ARITHMETIC =====
            if op in ["+", "-", "*", "/"]:

                # string + string
                if (
                    l == "string"
                    and r == "string"
                ):

                    if op == "+":
                        return "string"

                    raise SemanticError(
                        "invalid string operation"
                    )

                # invalid mix
                if "string" in (l, r):

                    raise SemanticError(
                        "type mismatch"
                    )

                # float priority
                if "float" in (l, r):
                    return "float"

                return "int"

            # ===== COMPARISON =====
            if op in [">", "<", "=="]:
                return "int"

        raise SemanticError(
            "invalid expression"
        )


# =========================================================
# WRAPPER
# =========================================================

# Job: run semantic analysis

def semantic_check(ast):

    Semantic().analyze(ast)