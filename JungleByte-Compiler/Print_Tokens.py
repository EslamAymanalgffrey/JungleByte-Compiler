def print_tokens_table_colored(tokens):
    print("\n\033[95m======================= BANANA TOKENS =======================\033[0m\n")

    # ===== HEADER =====
    header = f"{'Line':<6}{'Col':<6}{'Type':<15}{'Value'}"
    print("\033[96m" + header + "\033[0m")
    print("\033[90m" + "-" * 50 + "\033[0m")

    # ===== ROWS =====
    for line, col, ttype, value in [(t[2], t[3], t[0], t[1]) for t in tokens]:

        # ===== COLOR RULES =====
        if ttype in ["FUNCTION", "IF", "ELSE", "WHILE", "FOR", "RETURN"]:
            color = "\033[94m"   # blue (keywords)

        elif ttype in ["NUMBER", "FLOAT"]:
            color = "\033[93m"   # yellow (numbers)

        elif ttype == "STRING":
            color = "\033[92m"   # green (strings)

        elif ttype == "IDENTIFIER":
            color = "\033[97m"   # white

        elif ttype == "COMMENT":
            color = "\033[90m"   # gray

        else:
            color = "\033[91m"   # red (operators/symbols)

        # ===== PRINT ROW =====
        row = f"{line:<6}{col:<6}{ttype:<15}{value}"
        print(color + row + "\033[0m")