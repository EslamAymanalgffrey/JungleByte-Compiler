from Print_AST import *

# =========================================================
# PARSER
# =========================================================

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens
        self.pos = 0

    # =====================================================
    # CURRENT TOKEN
    # =====================================================

    def cur(self):

        if self.pos < len(self.tokens):
            return self.tokens[self.pos]

        return ("EOF", "", 0, 0)

    # =====================================================
    # SYNTAX ERROR
    # =====================================================

    def syntax_error(self, message, tok=None):

        if tok is None:
            tok = self.cur()

        if len(tok) == 4:
            ttype, value, line, col = tok
        else:
            ttype, value, line = tok
            col = 0

        msg = f"""
╔══════════════════════════════════════╗
║           SYNTAX ERROR              ║
╠══════════════════════════════════════╣

 Message : {message}

 Line    : {line}
 Column  : {col}
 Type    : {ttype}
 Value   : {value}

╚══════════════════════════════════════╝
"""

        raise Exception(msg)

    # =====================================================
    # EAT TOKEN
    # =====================================================

    def eat(self, t):

        tok = self.cur()

        if tok[0] == t:
            self.pos += 1
            return tok

        self.syntax_error(
            f"Expected {t}",
            tok
        )

    # =====================================================
    # MATCH TOKEN
    # =====================================================

    def match(self, t):

        if self.cur()[0] == t:
            self.pos += 1
            return True

        return False

    # =====================================================
    # ENTRY
    # =====================================================

    def parse(self):

        return self.parse_program()

    # =====================================================
    # PROGRAM
    # =====================================================

    def parse_program(self):

        items = []

        while self.cur()[0] != "EOF":
            if self.cur()[0] == "EMPTY":

                self.pos += 1
                continue

            if self.cur()[0] == "COMMENT":
                self.pos += 1
                continue

            if self.cur()[0] == "FUNCTION":
                items.append(self.parse_function())
            else:
                items.append(self.parse_stmt())

        return Program(items)

    # =====================================================
    # FUNCTION
    # =====================================================

    def parse_function(self):

        self.eat("FUNCTION")

        name = self.eat("IDENTIFIER")[1]

        self.eat("LPAREN")

        params = self.parse_params()

        self.eat("RPAREN")

        self.eat("COLON")

        body = self.parse_block()

        return Function(
            name,
            params,
            "int",
            body
        )

    # =====================================================
    # PARAMETERS
    # =====================================================

    def parse_params(self):

        params = []

        if self.cur()[0] != "RPAREN":

            while True:

                params.append(
                    self.eat("IDENTIFIER")[1]
                )

                if not self.match("COMMA"):
                    break

        return params

    # =====================================================
    # BLOCK
    # =====================================================

    def parse_block(self):
        # Job: skip empty lines before block

        while self.cur()[0] == "EMPTY":

            self.pos += 1

        self.eat("INDENT")

        stmts = []

        while self.cur()[0] != "DEDENT":
            if self.cur()[0] == "EMPTY":

                self.pos += 1
                continue

            if self.cur()[0] == "COMMENT":
                self.pos += 1
                continue

            stmts.append(
                self.parse_stmt()
            )

        self.eat("DEDENT")

        return Block(stmts)

    # =====================================================
    # STATEMENTS
    # =====================================================

    def parse_stmt(self):

        tok = self.cur()

        # RETURN
        if tok[0] == "RETURN":

            self.eat("RETURN")

            return Return(
                self.parse_expr()
            )

        # IDENTIFIER
        if tok[0] == "IDENTIFIER":

            next_tok = (
                self.tokens[self.pos + 1]
                if self.pos + 1 < len(self.tokens)
                else None
            )

            if next_tok and next_tok[0] == "LPAREN":
                return self.parse_call()

            return self.parse_assignment()

        # PRINT
        if tok[0] == "PRINT":

            self.eat("PRINT")

            return Print(
                self.parse_expr()
            )

        # IF
        if tok[0] == "IF":
            return self.parse_if()

        # WHILE
        if tok[0] == "WHILE":

            self.eat("WHILE")

            cond = self.parse_expr()

            self.eat("COLON")

            return While(
                cond,
                self.parse_block()
            )

        # FOR
        if tok[0] == "FOR":
            return self.parse_for()

        # BREAK
        if tok[0] == "BREAK":

            self.eat("BREAK")

            return Break()

        # CONTINUE
        if tok[0] == "CONTINUE":

            self.eat("CONTINUE")

            return Continue()

        self.syntax_error(
            "Invalid statement",
            tok
        )

    # =====================================================
    # CALL
    # =====================================================

    def parse_call(self):

        name = self.eat("IDENTIFIER")[1]

        self.eat("LPAREN")

        args = []

        if self.cur()[0] != "RPAREN":

            while True:

                args.append(
                    self.parse_expr()
                )

                if not self.match("COMMA"):
                    break

        self.eat("RPAREN")

        return Call(name, args)

    # =====================================================
    # ASSIGNMENT
    # =====================================================

    def parse_assignment(self):

        name = self.eat("IDENTIFIER")[1]

        tok = self.cur()

        # += -= *= /=
        if tok[0] == "OPERATOR" and tok[1] in [
            "+=",
            "-=",
            "*=",
            "/="
        ]:

            op = self.eat("OPERATOR")[1]

            expr = self.parse_expr()

            if op == "+=":
                return Assign(
                    name,
                    BinOp("+", name, expr)
                )

            elif op == "-=":
                return Assign(
                    name,
                    BinOp("-", name, expr)
                )

            elif op == "*=":
                return Assign(
                    name,
                    BinOp("*", name, expr)
                )

            elif op == "/=":
                return Assign(
                    name,
                    BinOp("/", name, expr)
                )

        # NORMAL ASSIGN
        if tok[0] == "OPERATOR" and tok[1] == "=":

            self.eat("OPERATOR")

            return Assign(
                name,
                self.parse_expr()
            )

        # ++ --
        if tok[0] == "OPERATOR" and tok[1] in [
            "++",
            "--"
        ]:

            op = self.eat("OPERATOR")[1]

            if op == "++":

                return Assign(
                    name,
                    BinOp("+", name, "1")
                )

            else:

                return Assign(
                    name,
                    BinOp("-", name, "1")
                )

        return name

    # =====================================================
    # IF
    # =====================================================

    def parse_if(self):

        branches = []

        self.eat("IF")

        cond = self.parse_expr()

        self.eat("COLON")

        branches.append(
            (
                cond,
                self.parse_block()
            )
        )

        while self.match("ELSE_IF"):

            cond = self.parse_expr()

            self.eat("COLON")

            branches.append(
                (
                    cond,
                    self.parse_block()
                )
            )

        else_block = None

        if self.match("ELSE"):

            self.eat("COLON")

            else_block = self.parse_block()

        return If(
            branches,
            else_block
        )

    # =====================================================
    # FOR
    # =====================================================

    def parse_for(self):

        self.eat("FOR")

        var = self.eat("IDENTIFIER")[1]

        self.eat("IN")

        self.eat("RANGE")

        self.eat("LPAREN")

        limit = self.parse_expr()

        self.eat("RPAREN")

        self.eat("COLON")

        return For(
            var,
            limit,
            self.parse_block()
        )

    # =====================================================
    # EXPRESSIONS
    # =====================================================

    def parse_expr(self):

        left = self.parse_term()

        while (
            self.cur()[0] == "OPERATOR"
            and
            self.cur()[1] in [
                "+",
                "-",
                ">",
                "<",
                "=="
            ]
        ):

            op = self.eat("OPERATOR")[1]

            right = self.parse_term()

            left = BinOp(
                op,
                left,
                right
            )

        return left

    # =====================================================
    # TERM
    # =====================================================

    def parse_term(self):

        left = self.parse_factor()

        while (
            self.cur()[0] == "OPERATOR"
            and
            self.cur()[1] in [
                "*",
                "/"
            ]
        ):

            op = self.eat("OPERATOR")[1]

            right = self.parse_factor()

            left = BinOp(
                op,
                left,
                right
            )

        return left

    # =====================================================
    # FACTOR
    # =====================================================

    def parse_factor(self):

        tok = self.cur()

        # LITERALS
        if tok[0] in [
            "NUMBER",
            "FLOAT",
            "STRING"
        ]:

            self.pos += 1

            return tok[1]

        # IDENTIFIER / CALL
        if tok[0] == "IDENTIFIER":

            next_tok = (
                self.tokens[self.pos + 1]
                if self.pos + 1 < len(self.tokens)
                else None
            )

            if next_tok and next_tok[0] == "LPAREN":
                return self.parse_call()

            return self.eat("IDENTIFIER")[1]

        # GROUPING
        if self.match("LPAREN"):

            expr = self.parse_expr()

            self.eat("RPAREN")

            return expr

        self.syntax_error(
            "Invalid expression",
            tok
        )