# =========================================================
# JUNGLEBYTE IDE V3
# =========================================================

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import io
import sys
import re

# =========================================================
# IMPORT COMPILER PHASES
# =========================================================

from Banana_Scanner import tokenize
from Monkey_Parser import Parser
from Semmantic import semantic_check
from CodeGen import generate_python

# =========================================================
# THEME
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# IDE
# =========================================================

class JungleByteIDE:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "🍌 JungleByte Compiler IDE • v3"
        )
        self.root.geometry("1650x900")

        # =====================================================
        # COLORS
        # =====================================================

        self.bg = "#0b1120"
        self.panel = "#111827"
        self.panel2 = "#161f33"
        self.editor_bg = "#0f172a"
        self.glow = "#00e5ff"
        self.purple = "#8b5cf6"

        self.cyan = "#38bdf8"
        self.green = "#22c55e"
        self.red = "#ef4444"
        self.yellow = "#facc15"
        self.pink = "#f472b6"
        self.gray = "#64748b"
        self.white = "#f8fafc"

        self.root.configure(fg_color=self.bg)

        # =====================================================
        # HEADER
        # =====================================================

        logo_shadow = ctk.CTkLabel(
            root,
            text="⬢",
            font=("Consolas", 72, "bold"),
            text_color="#6d28d9"
        )

        logo_shadow.place(
            relx=0.5,
            y=48,
            anchor="center"
        )

        logo = ctk.CTkLabel(
            root,
            text="⬢",
            font=("Consolas", 68, "bold"),
            text_color="#22d3ee"
        )

        logo.pack(
            pady=(5, 0)
        )

        shadow = ctk.CTkLabel(
            root,
            text="JungleByte",
            font=("Orbitron", 42, "bold"),
            text_color="#7c3aed"
        )

        shadow.place(
            relx=0.5,
            y=92,
            anchor="center"
        )

        title = ctk.CTkLabel(
            root,
            text="JungleByte",
            font=("Orbitron", 40, "bold"),
            text_color="#67e8f9"
        )

        title.pack(
            pady=(0, 0)
        )

        compiler = ctk.CTkLabel(
            root,
            text="◆ COMPILER IDE ◆",
            font=("Consolas", 16, "bold"),
            text_color="#f472b6"
        )

        compiler.pack()

        subtitle = ctk.CTkLabel(
            root,
            text="Lexer • Parser • AST • Semantic • Code Generation",
            font=("Consolas", 11),
            text_color="#64748b"
        )

        subtitle.pack(
            pady=(0, 14)
        )

        # =====================================================
        # MAIN FRAME
        # =====================================================

        main = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=(2, 4)
        )

        # =====================================================
        # LEFT SIDE
        # =====================================================

        left = ctk.CTkFrame(
            main,
            fg_color=self.panel,
            corner_radius=20,
            border_width=2,
            border_color="#1e293b"
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        source_label = ctk.CTkLabel(
            left,
            text="SOURCE CODE",
            font=("Consolas", 16, "bold"),
            text_color=self.yellow
        )

        source_label.pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )

        # =====================================================
        # EDITOR FRAME
        # =====================================================

        editor_frame = ctk.CTkFrame(
            left,
            fg_color=self.editor_bg,
            corner_radius=18,
            border_width=2,
            border_color="#1e293b"
        )

        editor_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=8
        )


        editor_top = ctk.CTkFrame(
            editor_frame,
            fg_color="#0b1220",
            height=38,
            corner_radius=10
        )

        editor_top.pack(fill="x", padx=8, pady=8)

        for color in ["#ef4444", "#facc15", "#22c55e"]:

            dot = ctk.CTkLabel(
                editor_top,
                text="●",
                text_color=color
            )

            dot.pack(side="left", padx=4)

        # =====================================================
        # LINE NUMBERS
        # =====================================================

        self.lines = tk.Text(
            editor_frame,
            width=4,
            bg="#020617",
            fg=self.gray,
            font=("Consolas", 14),
            bd=0,
            state="disabled"
        )

        self.lines.pack(
            side="left",
            fill="y"
        )

        # =====================================================
        # SOURCE EDITOR
        # =====================================================

        self.editor = ctk.CTkTextbox(
            editor_frame,
            font=("JetBrains Mono", 16),
            fg_color="#0b1120",
            text_color=self.white,
            border_color=self.glow,
            border_width=2
        )   

        self.editor.pack(
            side="right",
            fill="both",
            expand=True
        )

        # =====================================================
        # SYNTAX COLORS
        # =====================================================

        box = self.editor._textbox

        box.tag_config("keyword", foreground=self.cyan)
        box.tag_config("string", foreground=self.green)
        box.tag_config("number", foreground=self.yellow)
        box.tag_config("comment", foreground=self.gray)
        box.tag_config("operator", foreground=self.pink)

        # =====================================================
        # EVENTS
        # =====================================================

        self.editor.bind(
            "<KeyRelease>",
            self.update_all
        )

        # =====================================================
        # TAB = 4 SPACES
        # =====================================================

        self.editor.bind(
            "<Tab>",
            self.insert_tab
        )

        # =====================================================
        # DEMO CODE
        # =====================================================

        demo = '''# JungleByte Demo

climbUp main():

    x = 2

    ooh_ooh "Start"

    branchIf x > 3:
        ooh_ooh "Big"

    branchElse:
        ooh_ooh "Small"

    swing x < 5:
        ooh_ooh x
        x += 1

    climb i in range(3):
        ooh_ooh i
'''

        self.editor.insert("1.0", demo)

        self.update_all()

        # =====================================================
        # BUTTONS
        # =====================================================

        btn_frame = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )

        btn_frame.pack(
            fill="x",
            pady=5
        )

        self.run_btn = ctk.CTkButton(
            btn_frame,
            text="▶ COMPILE & RUN",
            command=self.run_compiler,
            fg_color=self.green,
            hover_color="#16a34a",
            font=("Consolas", 16, "bold"),
            height=36,
            corner_radius=10
        )

        self.run_btn.pack(
            side="left",
            padx=10
        )

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑 CLEAR",
            command=self.clear_outputs,
            fg_color=self.red,
            hover_color="#dc2626",
            font=("Consolas", 16, "bold"),
            height=42,
            corner_radius=10
        )

        clear_btn.pack(
            side="left"
        )

        # =====================================================
        # RIGHT SIDE
        # =====================================================

        right = ctk.CTkFrame(
            main,
            fg_color=self.panel,
            corner_radius=20,
            border_width=2,
            border_color="#1e293b"
        )

        right.pack(
            side="right",
            fill="both",
            expand=True
        )

        right.configure(width=560)


        # =====================================================
        # TABS
        # =====================================================

        
        output_bar = ctk.CTkFrame(
            right,
            fg_color="#111827",
            height=42,
            corner_radius=12
        )

        output_bar.pack(
            fill="x",
            padx=6,
            pady=(3, 2)
        )

        output_title = ctk.CTkLabel(
            output_bar,
            text="⚡ OUTPUT / TOKENS / AST",
            font=("JetBrains Mono", 17, "bold"),
            text_color=self.cyan
        )

        output_title.pack(
            side="left",
            padx=14,
            pady=8
        )

        self.tabs = ctk.CTkTabview(
            right,
            fg_color=self.panel,
            segmented_button_fg_color="#111827",
            segmented_button_selected_color=self.purple,
            segmented_button_selected_hover_color="#7c3aed",
            segmented_button_unselected_hover_color="#1e293b",
            corner_radius=18
        )

        self.tabs.pack(
            fill="both",
            expand=True,
            padx=4,
            pady=1
        )

        self.tabs.add("TOKENS")
        self.tabs.add("AST")
        self.tabs.add("SEMANTIC")
        self.tabs.add("PYTHON")
        self.tabs.add("OUTPUT")

        # =====================================================
        # TOKENS TABLE
        # =====================================================

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#0b1220",
            foreground="white",
            fieldbackground="#0b1220",
            rowheight=28,
            font=("Consolas", 11)
        )

        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground=self.cyan,
            font=("Consolas", 9, "bold")
        )

        self.tokens_table = ttk.Treeview(
            self.tabs.tab("TOKENS"),
            columns=("Line", "Col", "Type", "Value"),
            show="headings"
        )

        for col in ["Line", "Col", "Type", "Value"]:

            self.tokens_table.heading(
                col,
                text=col
            )

        self.tokens_table.column("Line", width=70)
        self.tokens_table.column("Col", width=70)
        self.tokens_table.column("Type", width=180)
        self.tokens_table.column("Value", width=350)

        self.tokens_table.pack(
            fill="both",
            expand=True
        )

        # =====================================================
        # OUTPUT BOXES
        # =====================================================

        self.ast_box = self.make_box("AST")
        self.semantic_box = self.make_box("SEMANTIC")
        self.python_box = self.make_box("PYTHON")
        self.output_box = self.make_box("OUTPUT")

        # =====================================================
        # STATUS
        # =====================================================

        self.status = ctk.CTkLabel(
            root,
            text="Ready",
            font=("Consolas", 12),
            text_color=self.green
        )

        self.status.pack(
            pady=5
        )

    # =========================================================
    # MAKE BOX
    # =========================================================

    def make_box(self, tab):

        box = ctk.CTkTextbox(
            self.tabs.tab(tab),
            font=("Consolas", 12),
            fg_color="#0b1220",
            text_color=self.white,
            border_color=self.cyan,
            border_width=1
        )

        box.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        return box

    # =========================================================
    # UPDATE
    # =========================================================

    def update_all(self, event=None):

        self.update_lines()
        self.highlight_syntax()

    # =========================================================
    # LINE NUMBERS
    # =========================================================

    def update_lines(self):

        text = self.editor.get(
            "1.0",
            "end-1c"
        )

        count = len(text.split("\n"))

        self.lines.config(state="normal")

        self.lines.delete(
            "1.0",
            tk.END
        )

        for i in range(1, count + 1):

            self.lines.insert(
                tk.END,
                f"{i}\n"
            )

        self.lines.config(state="disabled")

    # =========================================================
    # SYNTAX HIGHLIGHT
    # =========================================================

    def highlight_syntax(self):

        textbox = self.editor._textbox

        text = self.editor.get(
            "1.0",
            "end-1c"
        )

        # =====================================================
        # CLEAR OLD TAGS
        # =====================================================

        for tag in [
            "keyword",
            "string",
            "number",
            "comment",
            "operator"
        ]:

            textbox.tag_remove(
                tag,
                "1.0",
                tk.END
            )

        # =====================================================
        # KEYWORDS
        # =====================================================

        keywords = [
            "climbUp",
            "branchIf",
            "branchElse",
            "branchElseIf",
            "swing",
            "climb",
            "throwBananas",
            "ooh_ooh"
        ]

        # =====================================================
        # OPERATORS
        # =====================================================

        operators = [
            "+=",
            "-=",
            "*=",
            "/=",
            "++",
            "--",
            "+",
            "-",
            "*",
            "/",
            "=",
            "<",
            ">",
            "=="
        ]

        # =====================================================
        # LINE LOOP
        # =====================================================

        lines = text.split("\n")

        for row, line in enumerate(lines, start=1):

            # =================================================
            # SINGLE LINE COMMENTS
            # =================================================

            if "#" in line:

                idx = line.index("#")

                textbox.tag_add(
                    "comment",
                    f"{row}.{idx}",
                    f"{row}.{len(line)}"
                )

            # =================================================
            # STRINGS
            # =================================================

            for m in re.finditer(
                r'"[^"]*"',
                line
            ):

                textbox.tag_add(
                    "string",
                    f"{row}.{m.start()}",
                    f"{row}.{m.end()}"
                )

            # =================================================
            # NUMBERS
            # =================================================

            for m in re.finditer(
                r'\b\d+(\.\d+)?\b',
                line
            ):

                textbox.tag_add(
                    "number",
                    f"{row}.{m.start()}",
                    f"{row}.{m.end()}"
                )

            # =================================================
            # KEYWORDS
            # =================================================

            for word in keywords:

                for m in re.finditer(
                    rf'\b{word}\b',
                    line
                ):

                    textbox.tag_add(
                        "keyword",
                        f"{row}.{m.start()}",
                        f"{row}.{m.end()}"
                    )

            # =================================================
            # OPERATORS
            # =================================================

            for op in operators:

                for m in re.finditer(
                    re.escape(op),
                    line
                ):

                    textbox.tag_add(
                        "operator",
                        f"{row}.{m.start()}",
                        f"{row}.{m.end()}"
                    )

        # =====================================================
        # MULTI-LINE COMMENTS
        # =====================================================

        for m in re.finditer(
            r"'''(.*?)'''",
            text,
            re.DOTALL
        ):

            start = m.start()
            end = m.end()

            start_line = text.count(
                "\n",
                0,
                start
            ) + 1

            start_col = start - (
                text.rfind(
                    "\n",
                    0,
                    start
                ) + 1
            )

            end_line = text.count(
                "\n",
                0,
                end
            ) + 1

            end_col = end - (
                text.rfind(
                    "\n",
                    0,
                    end
                ) + 1
            )

            textbox.tag_add(
                "comment",
                f"{start_line}.{start_col}",
                f"{end_line}.{end_col}"
            )
            
        # =========================================================
        # CLEAR
        # =========================================================

    def clear_outputs(self):

        for item in self.tokens_table.get_children():
            self.tokens_table.delete(item)

        self.ast_box.delete("1.0", tk.END)
        self.semantic_box.delete("1.0", tk.END)
        self.python_box.delete("1.0", tk.END)
        self.output_box.delete("1.0", tk.END)

    # =========================================================
    # AST TO TEXT
    # =========================================================

    def ast_to_text(self, node, prefix="", is_last=True):

        connector = "└── " if is_last else "├── "

        if isinstance(node, tuple):

            text = prefix + connector + str(node[0]) + "\n"

            children = node[1:]

            for i, child in enumerate(children):

                last = i == len(children) - 1

                new_prefix = prefix + (
                    "    " if is_last else "│   "
                )

                text += self.ast_to_text(
                    child,
                    new_prefix,
                    last
                )

            return text

        elif isinstance(node, list):

            text = ""

            for i, item in enumerate(node):

                last = i == len(node) - 1

                text += self.ast_to_text(
                    item,
                    prefix,
                    last
                )

            return text

        else:
            return prefix + connector + str(node) + "\n"

    # =========================================================
    # SHOW ERROR
    # =========================================================

    def show_error(self, error):

        self.output_box.delete("1.0", tk.END)

        self.output_box.insert(
            "1.0",
            f"✖ ERROR\n\n{error}"
        )

        self.output_box.configure(
            text_color=self.red
        )

        self.status.configure(
            text="Compiler Error",
            text_color=self.red
        )

    # =========================================================
    # RUN COMPILER
    # =========================================================

    def run_compiler(self):

        self.clear_outputs()

        self.run_btn.configure(
            text="⏳ Compiling..."
        )

        try:

            code = self.editor.get(
                "1.0",
                tk.END
            )

            # =================================================
            # TOKENS
            # =================================================

            tokens = tokenize(code)

            # ===== TOKEN COLORS =====

            self.tokens_table.tag_configure(
                "keyword",
                foreground=self.cyan
            )

            self.tokens_table.tag_configure(
                "string",
                foreground=self.green
            )

            self.tokens_table.tag_configure(
                "number",
                foreground=self.yellow
            )

            self.tokens_table.tag_configure(
                "comment",
                foreground=self.gray
            )

            self.tokens_table.tag_configure(
                "operator",
                foreground=self.pink
            )

            self.tokens_table.tag_configure(
                "identifier",
                foreground=self.white
            )

            for t in tokens:

                if len(t) == 4:
                    ttype, value, line, col = t
                else:
                    ttype, value, line = t
                    col = "-"

                # ===== TAG TYPE =====

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

                    tag = "keyword"

                elif ttype in [
                    "NUMBER",
                    "FLOAT"
                ]:

                    tag = "number"

                elif ttype == "STRING":

                    tag = "string"

                elif ttype == "COMMENT":

                    tag = "comment"

                elif ttype == "IDENTIFIER":

                    tag = "identifier"

                else:

                    tag = "operator"

                self.tokens_table.insert(
                    "",
                    tk.END,
                    values=(line, col, ttype, value),
                    tags=(tag,)
                )

            # =================================================
            # PARSER
            # =================================================

            parser = Parser(tokens)

            ast = parser.parse()

            ast_text = self.ast_to_text(ast)

            self.ast_box.insert(
                "1.0",
                ast_text
            )

            # ===== AST STYLE =====

            self.ast_box.configure(
                font=("Consolas", 14),
                text_color=self.cyan
            )

            # =================================================
            # SEMANTIC
            # =================================================

            try:

                semantic_check(ast)

                self.semantic_box.insert(
                    "1.0",
                    "✔ Semantic Analysis Passed"
                )

                self.semantic_box.configure(
                    font=("Consolas", 15, "bold"),
                    text_color=self.green
                )

            except Exception as sem_error:

                # ===== TRY GET LAST TOKEN =====

                last_token = None

                try:
                    if tokens:
                        last_token = tokens[-1]
                except:
                    pass

                error_msg = "\n╔══════════════════════════════════════╗\n"
                error_msg += "║          SEMANTIC ERROR             ║\n"
                error_msg += "╠══════════════════════════════════════╣\n\n"

                error_msg += f" Message : {sem_error}\n\n"

                if last_token:

                    if len(last_token) == 4:
                        ttype, value, line, col = last_token
                    else:
                        ttype, value, line = last_token
                        col = "-"

                    error_msg += f" Line    : {line}\n"
                    error_msg += f" Column  : {col}\n"
                    error_msg += f" Type    : {ttype}\n"
                    error_msg += f" Value   : {value}\n"

                error_msg += "\n╚══════════════════════════════════════╝\n"

                self.semantic_box.insert(
                    "1.0",
                    error_msg
                )

                self.semantic_box.configure(
                    font=("Consolas", 14, "bold"),
                    text_color=self.red
                )

                self.status.configure(
                    text="Semantic Error",
                    text_color=self.red
                )

                self.run_btn.configure(
                    text="▶ Run Compiler"
                )

                return

            # =================================================
            # CODE GENERATION
            # =================================================

            py_code = generate_python(ast)

            self.python_box.insert(
                "1.0",
                py_code
            )

            py = self.python_box._textbox

            self.python_box.configure(
                font=("Consolas", 14)
            )

            # ===== PYTHON COLORS =====

            py.tag_config(
                "keyword",
                foreground=self.cyan
            )

            py.tag_config(
                "string",
                foreground=self.green
            )

            py.tag_config(
                "number",
                foreground=self.yellow
            )

            py.tag_config(
                "func",
                foreground=self.pink
            )

            py_keywords = [
                "def",
                "if",
                "else",
                "while",
                "for",
                "return",
                "print",
                "in"
            ]

            lines = py_code.split("\n")

            for row, line in enumerate(lines, start=1):

                # ===== KEYWORDS =====

                for word in py_keywords:

                    for m in re.finditer(
                        rf'\\b{word}\\b',
                        line
                    ):

                        py.tag_add(
                            "keyword",
                            f"{row}.{m.start()}",
                            f"{row}.{m.end()}"
                        )

                # ===== STRINGS =====

                for m in re.finditer(
                    r'\".*?\"',
                    line
                ):

                    py.tag_add(
                        "string",
                        f"{row}.{m.start()}",
                        f"{row}.{m.end()}"
                    )

                # ===== NUMBERS =====

                for m in re.finditer(
                    r'\\b\\d+(\\.\\d+)?\\b',
                    line
                ):

                    py.tag_add(
                        "number",
                        f"{row}.{m.start()}",
                        f"{row}.{m.end()}"
                    )

              # =================================================
            # EXECUTION
            # =================================================
            old_stdout = sys.stdout

            mystdout = io.StringIO()

            sys.stdout = mystdout

            # ===== EXECUTION NAMESPACE =====
            namespace = { "__name__": "__main__" } 

            # ===== EXECUTE GENERATED PYTHON =====
            exec(py_code, namespace)

            # ===== RESTORE STDOUT =====
            sys.stdout = old_stdout

            # ===== GET OUTPUT =====
            result = mystdout.getvalue()

            # ===== SHOW OUTPUT =====
            self.output_box.insert(
                "1.0",
                result
            )

            self.output_box.configure(
                font=("Consolas", 15, "bold")
            )

            out = self.output_box._textbox

            out.tag_config(
                "number",
                foreground=self.yellow
            )

            out.tag_config(
                "text",
                foreground=self.green
            )

            for row, line in enumerate(
                result.split("\n"),
                start=1
            ):

                if any(c.isdigit() for c in line):

                    out.tag_add(
                        "number",
                        f"{row}.0",
                        f"{row}.end"
                    )

                else:

                    out.tag_add(
                        "text",
                        f"{row}.0",
                        f"{row}.end"
                    )

            # =================================================
            # STATUS
            # =================================================

            self.status.configure(
                text=f"✔ Compilation Successful | Tokens: {len(tokens)}",
                text_color=self.green
            )

        except Exception as e:
            self.show_error(str(e))

        self.run_btn.configure(
            text="▶ Run Compiler"
        )

    # =========================================================
    # INSERT 4 SPACES
    # =========================================================

    def insert_tab(self, event):

        self.editor.insert(
            "insert",
            "    "
        )
        return "break"

# =========================================================
# MAIN
# =========================================================

root = ctk.CTk()

app = JungleByteIDE(root)

footer = ctk.CTkLabel(
    root,
    text="JungleByte Language • Custom Compiler Front-End",
    text_color=app.gray,
    font=("Consolas", 11)
)

footer.pack(
    pady=(0, 5)
)

root.mainloop()