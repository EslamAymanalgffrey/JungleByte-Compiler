import re

# Job: map language keywords
KEYWORDS = {

    "climbUp": "FUNCTION",

    "ooh_ooh": "PRINT",

    "branchIf": "IF",

    "branchElseIf": "ELSE_IF",

    "branchElse": "ELSE",

    "swing": "WHILE",

    "climb": "FOR",

    "throwBananas": "RETURN",

    "in": "IN",

    "range": "RANGE",

    "break": "BREAK",

    "continue": "CONTINUE"
}


# Job: define token patterns
TOKEN_REGEX = r"""
(?P<WHITESPACE>[ \t]+)
|(?P<COMMENT>\#.*)
|(?P<FLOAT>\d+\.\d+)
|(?P<NUMBER>\d+)
|(?P<STRING>"[^"\n]*")
|(?P<OPERATOR>\+\+|\-\-|\+=|\-=|\*=|\/=|==|!=|>=|<=|[+\-*/=<>])
|(?P<LPAREN>\()
|(?P<RPAREN>\))
|(?P<LBRACE>\{)
|(?P<RBRACE>\})
|(?P<LBRACKET>\[)
|(?P<RBRACKET>\])
|(?P<COMMA>,)
|(?P<COLON>:)
|(?P<IDENTIFIER>[a-zA-Z_][a-zA-Z0-9_]*)
|(?P<NEWLINE>\n)
"""


# Job: compile regex once
MASTER_RE = re.compile(
    TOKEN_REGEX,
    re.VERBOSE
)


# Job: convert source code into tokens
def tokenize(code):

    # Job: store tokens
    tokens = []

    # Job: remove multi-line comments
    while "'''" in code:

        start = code.find("'''")

        end = code.find(
            "'''",
            start + 3
        )

        if end == -1:

            raise Exception(
                "Unclosed multi-line comment"
            )

        code = (
            code[:start]
            +
            code[end + 3:]
        )

    # Job: track indentation levels
    indent_stack = [0]

    # Job: split source into lines
    lines = code.splitlines()

    # Job: process each line
    for line_no, line in enumerate(
        lines,
        start=1
    ):

        # Job: preserve empty lines
        if line.strip() == "":

            tokens.append(
                (
                    "EMPTY",
                    "",
                    line_no,
                    0
                )
            )

            continue

        # Job: calculate indentation
        stripped = line.lstrip(" ")

        indent = len(line) - len(stripped)

        # Job: enter new block
        if indent > indent_stack[-1]:

            indent_stack.append(indent)

            tokens.append(
                (
                    "INDENT",
                    indent,
                    line_no,
                    0
                )
            )

        # Job: exit block
        while indent < indent_stack[-1]:

            indent_stack.pop()

            tokens.append(
                (
                    "DEDENT",
                    indent,
                    line_no,
                    0
                )
            )

        # Job: scan line characters
        pos = 0

        while pos < len(line):

            # Job: match token
            match = MASTER_RE.match(
                line,
                pos
            )

            # Job: lexical error handling
            if not match:

                raise Exception(
                    f"Lexical Error at "
                    f"line {line_no}, "
                    f"col {pos}"
                )

            # Job: extract token info
            kind = match.lastgroup

            value = match.group()

            col = match.start()

            # Job: ignore spaces
            if kind == "WHITESPACE":

                pos = match.end()

                continue

            # Job: handle comments
            if kind == "COMMENT":

                tokens.append(
                    (
                        "COMMENT",
                        value,
                        line_no,
                        col
                    )
                )

                break

            # Job: convert identifier into keyword
            if kind == "IDENTIFIER":

                if value in KEYWORDS:

                    kind = KEYWORDS[value]

            # Job: save token
            tokens.append(
                (
                    kind,
                    value,
                    line_no,
                    col
                )
            )

            # Job: move scanner forward
            pos = match.end()

    # Job: close remaining blocks
    while len(indent_stack) > 1:

        indent_stack.pop()

        tokens.append(
            (
                "DEDENT",
                0,
                line_no,
                0
            )
        )

    # Job: return all tokens
    return tokens
