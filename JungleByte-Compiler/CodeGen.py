# ===== PYTHON CODE GENERATOR =====
# Job: convert AST → executable Python code

class PyCodeGen:

    def __init__(self):

        # Job: generated python lines
        self.code = []

        # Job: indentation level
        self.indent = 0


# =========================================================
# HELPERS
# =========================================================

    # Job: emit line with indentation
    def emit(self, line):
        self.code.append(
            "    " * self.indent + line
        )

    # Job: increase indentation
    def inc(self):
        self.indent += 1

    # Job: decrease indentation
    def dec(self):
        self.indent -= 1


# =========================================================
# ENTRY
# =========================================================

    # Job: generate full program
    def generate(self, ast):

        _, items = ast

        functions = []
        statements = []

        # ===== SPLIT =====
        for item in items:

            if item[0] == "FUNCTION":
                functions.append(item)

            else:
                statements.append(item)

        # ===== GENERATE FUNCTIONS =====
        for func in functions:
            self.visit(func)

        # ===== MAIN BLOCK =====
        self.emit("")
        self.emit("if __name__ == '__main__':")

        self.inc()

        # ===== GLOBAL STATEMENTS =====
        for stmt in statements:
            self.visit(stmt)

        # ===== AUTO MAIN =====
        if any(
            f[0] == "FUNCTION"
            and f[1] == "main"
            for f in functions
        ):
            self.emit("main()")

        self.dec()

        return "\n".join(self.code)


# =========================================================
# DISPATCH
# =========================================================

    # Job: dispatch node
    def visit(self, node):

        t = node[0]

        # ===== FUNCTION =====
        if t == "FUNCTION":
            self.gen_function(node)

        # ===== ASSIGN =====
        elif t == "ASSIGN":

            _, name, expr = node

            self.emit(
                f"{name} = {self.expr(expr)}"
            )

        # ===== PRINT =====
        elif t == "PRINT":

            self.emit(
                f"print({self.expr(node[1])})"
            )

        # ===== CALL =====
        elif t == "CALL":

            self.emit(
                self.call(node)
            )

        # ===== RETURN =====
        elif t == "RETURN":

            self.emit(
                f"return {self.expr(node[1])}"
            )

        # ===== IF =====
        elif t == "IF":
            self.gen_if(node)

        # ===== WHILE =====
        elif t == "WHILE":
            self.gen_while(node)

        # ===== FOR =====
        elif t == "FOR":
            self.gen_for(node)

        # ===== CONTINUE =====
        elif t == "CONTINUE":
            self.emit("continue")

        # ===== BREAK =====
        elif t == "BREAK":
            self.emit("break")


# =========================================================
# FUNCTION
# =========================================================

    # Job: generate function
    def gen_function(self, node):

        _, name, params, _, body = node

        params_str = ", ".join(params)

        self.emit(
            f"def {name}({params_str}):"
        )

        self.inc()

        # ===== EMPTY BODY =====
        if not body[1]:

            self.emit("pass")

        else:

            for stmt in body[1]:
                self.visit(stmt)

        self.dec()

        self.emit("")


# =========================================================
# IF
# =========================================================

    # Job: generate if/elif/else
    def gen_if(self, node):

        branches, else_block = node[1], node[2]

        for i, (cond, block) in enumerate(branches):

            keyword = (
                "if"
                if i == 0
                else "elif"
            )

            self.emit(
                f"{keyword} {self.expr(cond)}:"
            )

            self.inc()

            for stmt in block[1]:
                self.visit(stmt)

            self.dec()

        # ===== ELSE =====
        if else_block:

            self.emit("else:")

            self.inc()

            for stmt in else_block[1]:
                self.visit(stmt)

            self.dec()


# =========================================================
# WHILE
# =========================================================

    # Job: generate while
    def gen_while(self, node):

        _, cond, body = node

        self.emit(
            f"while {self.expr(cond)}:"
        )

        self.inc()

        for stmt in body[1]:
            self.visit(stmt)

        self.dec()


# =========================================================
# FOR
# =========================================================

    # Job: generate for loop
    def gen_for(self, node):

        _, var, limit, body = node

        self.emit(
            f"for {var} in range({self.expr(limit)}):"
        )

        self.inc()

        for stmt in body[1]:
            self.visit(stmt)

        self.dec()


# =========================================================
# EXPRESSIONS
# =========================================================

    # Job: expression → python
    def expr(self, expr):

        # ===== STRING / NUMBER / VAR =====
        if isinstance(expr, str):
            return expr

        # ===== FUNCTION CALL =====
        if expr[0] == "CALL":
            return self.call(expr)

        # ===== BIN OP =====
        if expr[0] == "BIN_OP":

            _, op, left, right = expr

            return (
                f"({self.expr(left)} "
                f"{op} "
                f"{self.expr(right)})"
            )

        return str(expr)


# =========================================================
# CALL
# =========================================================

    # Job: generate function call
    def call(self, node):

        _, name, args = node

        args_str = ", ".join(
            self.expr(a)
            for a in args
        )

        return f"{name}({args_str})"


# =========================================================
# WRAPPER
# =========================================================

# Job: generate python code

def generate_python(ast):

    gen = PyCodeGen()

    return gen.generate(ast)
