# =========================================================
# JUNGLEBYTE COMPILER
# =========================================================

from Banana_Scanner import tokenize
from Monkey_Parser import Parser
from Print_AST import print_tree
from Semmantic import semantic_check
from CodeGen import generate_python

import os


# =========================================================
# COLORS
# =========================================================

RESET   = "\033[0m"

RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
GRAY    = "\033[90m"


# =========================================================
# TERMINAL HEADER
# =========================================================

def banner():

    print(MAGENTA)

    print("╔══════════════════════════════════════════════╗")
    print("║           🍌 JUNGLEBYTE COMPILER            ║")
    print("║         Scanner • Parser • AST              ║")
    print("╚══════════════════════════════════════════════╝")

    print(RESET)


# =========================================================
# SECTION TITLE
# =========================================================

def section(title):

    print(
        f"\n{MAGENTA}"
        f"{'=' * 20} "
        f"{title} "
        f"{'=' * 20}"
        f"{RESET}\n"
    )


# =========================================================
# TOKEN COLORS
# =========================================================

def token_color(ttype):

    if ttype in [
        "FUNCTION",
        "IF",
        "ELSE",
        "ELSE_IF",
        "WHILE",
        "FOR",
        "RETURN",
        "PRINT"
    ]:
        return BLUE

    elif ttype in [
        "NUMBER",
        "FLOAT"
    ]:
        return YELLOW

    elif ttype == "STRING":
        return GREEN

    elif ttype == "COMMENT":
        return GRAY

    elif ttype == "IDENTIFIER":
        return WHITE

    return RED


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():

    os.system("cls")

    banner()

    # =====================================================
    # READ SOURCE FILE
    # =====================================================

    section("SOURCE")

    with open("test.jb") as f:

        code = f.read()

    print(
        GREEN +
        "✔ Source Loaded" +
        RESET
    )

    # =====================================================
    # SCANNER
    # =====================================================

    section("TOKENS")

    tokens = tokenize(code)

    header = (
        f"{'Line':<6}"
        f"{'Col':<6}"
        f"{'Type':<15}"
        f"{'Value'}"
    )

    print(CYAN + header + RESET)

    print(GRAY + "-" * 60 + RESET)

    for t in tokens:

        if t[0] in [
            "EMPTY",
            "INDENT",
            "DEDENT"
        ]:
            continue

        ttype, value, line, col = t

        color = token_color(ttype)

        print(
            color +
            f"{line:<6}"
            f"{col:<6}"
            f"{ttype:<15}"
            f"{value}" +
            RESET
        )

    # =====================================================
    # PARSER
    # =====================================================

    section("PARSER")

    parser = Parser(tokens)

    ast = parser.parse()

    print(
        GREEN +
        "✔ Parsing Completed" +
        RESET
    )

    # =====================================================
    # AST
    # =====================================================

    section("AST")

    print_tree(ast)

    # =====================================================
    # SEMANTIC ANALYSIS
    # =====================================================

    section("SEMANTIC")

    try:

        semantic_check(ast)

        print(
            GREEN +
            "✔ Semantic Analysis Passed" +
            RESET
        )

    except Exception as e:

        print(
            RED +
            f"✖ Semantic Error: {e}" +
            RESET
        )

        return

    # =====================================================
    # CODE GENERATION
    # =====================================================

    section("GENERATED PYTHON")

    py_code = generate_python(ast)

    print(py_code)

    # =====================================================
    # EXECUTION
    # =====================================================

    section("PROGRAM OUTPUT")

    exec(
        py_code,
        {
            "__name__": "__main__"
        }
    )


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":

    main()
