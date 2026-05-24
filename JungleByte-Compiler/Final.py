# =========================================================
# JUNGLEBYTE IDE V3 - PERFECT SIZING & COLORED TOKENS
# =========================================================

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import io
import sys
import re

# =========================================================
# IMPORT COMPILER PHASES (Logic exactly preserved)
# =========================================================
from Banana_Scanner import tokenize
from Monkey_Parser import Parser
from Semmantic import semantic_check
from CodeGen import generate_python

# =========================================================
# THEME SETUP
# =========================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JungleByteIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("🍌 JungleByte Compiler IDE")
        self.root.geometry("1450x850")

        # =====================================================
        # EXACT ORIGINAL COLORS
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
        # TOP HEADER BAR
        # =====================================================
        self.header = ctk.CTkFrame(self.root, height=70, fg_color=self.panel, corner_radius=0)
        self.header.pack(fill="x", side="top")

        brand_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=10)
        
        logo = ctk.CTkLabel(brand_frame, text="⬢", font=("Consolas", 36, "bold"), text_color=self.purple)
        logo.pack(side="left", padx=(0, 10))
        
        title = ctk.CTkLabel(brand_frame, text="JungleByte", font=("Orbitron", 24, "bold"), text_color=self.cyan)
        title.pack(side="left")

        subtitle = ctk.CTkLabel(brand_frame, text="COMPILER SUITE", font=("Consolas", 12, "bold"), text_color=self.gray)
        subtitle.pack(side="left", padx=10, pady=(8, 0))

        btn_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)

        self.clear_btn = ctk.CTkButton(btn_frame, text="🗑 CLEAR", command=self.clear_outputs, 
                                       fg_color="transparent", border_width=1, border_color=self.red, 
                                       hover_color="#451a1a", text_color=self.red, font=("Consolas", 14, "bold"), width=100)
        self.clear_btn.pack(side="left", padx=10)

        self.run_btn = ctk.CTkButton(btn_frame, text="▶ COMPILE & RUN", command=self.run_compiler, 
                                     fg_color=self.green, hover_color="#16a34a", text_color="black", 
                                     font=("Consolas", 14, "bold"), width=160, height=36)
        self.run_btn.pack(side="left")

        # =====================================================
        # MAIN WORKSPACE SPLIT (GRID FOR PERFECT SIZING)
        # =====================================================
        self.workspace = ctk.CTkFrame(self.root, fg_color="transparent")
        self.workspace.pack(fill="both", expand=True, padx=15, pady=15)

        # Proportional Columns: 60% Left (Editor), 40% Right (Outputs)
        self.workspace.grid_columnconfigure(0, weight=6)
        self.workspace.grid_columnconfigure(1, weight=4)
        self.workspace.grid_rowconfigure(0, weight=1)

        # LEFT PANE: Editor
        self.left_pane = ctk.CTkFrame(self.workspace, fg_color=self.editor_bg, corner_radius=12, border_width=1, border_color=self.panel2)
        self.left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # RIGHT PANE: Outputs
        self.right_pane = ctk.CTkFrame(self.workspace, fg_color=self.panel, corner_radius=12, border_width=1, border_color=self.panel2)
        self.right_pane.grid(row=0, column=1, sticky="nsew")

        self.setup_editor()
        self.setup_output_tabs()

        # =====================================================
        # STATUS BAR
        # =====================================================
        self.status_bar = ctk.CTkFrame(self.root, height=30, fg_color=self.panel, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_lbl = ctk.CTkLabel(self.status_bar, text="🟢 System Ready", font=("Consolas", 12), text_color=self.green)
        self.status_lbl.pack(side="left", padx=20)

    # =========================================================
    # EDITOR SETUP
    # =========================================================
    def setup_editor(self):
        editor_header = ctk.CTkFrame(self.left_pane, fg_color="transparent", height=35)
        editor_header.pack(fill="x", padx=15, pady=10)
        
        for color in [self.red, self.yellow, self.green]:
            dot = ctk.CTkLabel(editor_header, text="●", text_color=color, font=("Consolas", 14))
            dot.pack(side="left", padx=2)
            
        file_lbl = ctk.CTkLabel(editor_header, text="source.jb", font=("Consolas", 12, "italic"), text_color=self.gray)
        file_lbl.pack(side="left", padx=15)

        edit_container = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        edit_container.pack(fill="both", expand=True, padx=2, pady=(0, 10))

        self.lines = tk.Text(edit_container, width=4, bg=self.editor_bg, fg=self.gray, font=("Consolas", 15), bd=0, state="disabled")
        self.lines.pack(side="left", fill="y", padx=(5, 0))

        self.editor = ctk.CTkTextbox(edit_container, font=("Consolas", 15), fg_color="transparent", text_color=self.white, wrap="none")
        self.editor.pack(side="right", fill="both", expand=True, padx=5)

        self.editor.bind("<KeyRelease>", self.update_all)
        self.editor.bind("<Tab>", self.insert_tab)
        self.setup_syntax_tags()
        self.load_demo_code()

    # =========================================================
    # OUTPUT TABS SETUP
    # =========================================================
    def setup_output_tabs(self):
        self.tabs = ctk.CTkTabview(self.right_pane, fg_color="transparent", 
                                   segmented_button_selected_color=self.purple,
                                   segmented_button_unselected_color=self.panel,
                                   segmented_button_fg_color=self.panel2,
                                   text_color=self.white)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

        for tab_name in ["OUTPUT", "TOKENS", "AST", "SEMANTIC", "PYTHON"]:
            self.tabs.add(tab_name)

        self.output_box = self.create_styled_box("OUTPUT", text_color="#f8fafc", bg_color="#000000", font=("Consolas", 14))
        self.ast_box = self.create_styled_box("AST", text_color=self.cyan, bg_color=self.bg, font=("Consolas", 14))
        self.semantic_box = self.create_styled_box("SEMANTIC", text_color=self.green, bg_color=self.panel2, font=("Consolas", 14, "bold"))
        self.python_box = self.create_styled_box("PYTHON", text_color="#e2e8f0", bg_color="#1e293b", font=("Consolas", 14))
        
        self.setup_tokens_table()

    def create_styled_box(self, tab, text_color, bg_color, font):
        box = ctk.CTkTextbox(self.tabs.tab(tab), font=font, fg_color=bg_color, text_color=text_color, 
                             corner_radius=8, border_width=1, border_color="#334155")
        box.pack(fill="both", expand=True, pady=5)
        return box

    # =========================================================
    # PLUS-SIZED & COLORED TOKENS TABLE
    # =========================================================
    def setup_tokens_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # 1. Plus-Size styling for the Treeview
        style.configure("Treeview", 
                        background=self.bg, 
                        foreground=self.white, 
                        fieldbackground=self.bg, 
                        rowheight=35,           # Increased row height
                        borderwidth=0, 
                        font=("Consolas", 13))  # Increased font size
                        
        style.configure("Treeview.Heading", 
                        background=self.panel2, 
                        foreground=self.cyan, 
                        font=("Consolas", 13, "bold"), # Increased header font
                        borderwidth=0)
                        
        style.map("Treeview", background=[('selected', self.purple)])

        tree_frame = ctk.CTkFrame(self.tabs.tab("TOKENS"), fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, pady=5)

        self.tokens_table = ttk.Treeview(tree_frame, columns=("Line", "Col", "Type", "Value"), show="headings")
        
        # 2. Wider columns for the plus-size feel
        for col, width in zip(["Line", "Col", "Type", "Value"], [60, 60, 180, 280]):
            self.tokens_table.heading(col, text=col)
            self.tokens_table.column(col, width=width, anchor="center" if col in ["Line", "Col"] else "w")
        
        # 3. Configure colors for specific token tags
        self.tokens_table.tag_configure("keyword", foreground=self.cyan)
        self.tokens_table.tag_configure("string", foreground=self.green)
        self.tokens_table.tag_configure("number", foreground=self.yellow)
        self.tokens_table.tag_configure("comment", foreground=self.gray)
        self.tokens_table.tag_configure("operator", foreground=self.pink)
        self.tokens_table.tag_configure("identifier", foreground=self.white)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tokens_table.yview)
        self.tokens_table.configure(yscrollcommand=scrollbar.set)
        
        self.tokens_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # =========================================================
    # PRESERVED SYNTAX & LOGIC 
    # =========================================================
    def setup_syntax_tags(self):
        box = self.editor._textbox
        box.tag_config("keyword", foreground=self.cyan)
        box.tag_config("string", foreground=self.green)
        box.tag_config("number", foreground=self.yellow)
        box.tag_config("comment", foreground=self.gray)
        box.tag_config("operator", foreground=self.pink)

    def update_all(self, event=None):
        self.update_lines()
        self.highlight_syntax()

    def update_lines(self):
        text = self.editor.get("1.0", "end-1c")
        count = len(text.split("\n"))
        self.lines.config(state="normal")
        self.lines.delete("1.0", tk.END)
        for i in range(1, count + 1):
            self.lines.insert(tk.END, f"{i}\n")
        self.lines.config(state="disabled")

    def highlight_syntax(self):
        textbox = self.editor._textbox
        text = self.editor.get("1.0", "end-1c")
        for tag in ["keyword", "string", "number", "comment", "operator"]:
            textbox.tag_remove(tag, "1.0", tk.END)

        keywords = ["climbUp", "branchIf", "branchElse", "branchElseIf", "swing", "climb", "throwBananas", "ooh_ooh"]
        operators = ["+=", "-=", "*=", "/=", "++", "--", "+", "-", "*", "/", "=", "<", ">", "=="]

        lines = text.split("\n")
        for row, line in enumerate(lines, start=1):
            if "#" in line:
                idx = line.index("#")
                textbox.tag_add("comment", f"{row}.{idx}", f"{row}.{len(line)}")
            for m in re.finditer(r'"[^"]*"', line):
                textbox.tag_add("string", f"{row}.{m.start()}", f"{row}.{m.end()}")
            for m in re.finditer(r'\b\d+(\.\d+)?\b', line):
                textbox.tag_add("number", f"{row}.{m.start()}", f"{row}.{m.end()}")
            for word in keywords:
                for m in re.finditer(rf'\b{word}\b', line):
                    textbox.tag_add("keyword", f"{row}.{m.start()}", f"{row}.{m.end()}")
            for op in operators:
                for m in re.finditer(re.escape(op), line):
                    textbox.tag_add("operator", f"{row}.{m.start()}", f"{row}.{m.end()}")

    def load_demo_code(self):
        demo = '''# JungleByte Demo\nclimbUp main():\n    x = 2\n    ooh_ooh "Start"\n\n    branchIf x > 3:\n        ooh_ooh "Big"\n    branchElse:\n        ooh_ooh "Small"\n\n    swing x < 5:\n        ooh_ooh x\n        x += 1\n'''
        self.editor.insert("1.0", demo)
        self.update_all()

    def clear_outputs(self):
        for item in self.tokens_table.get_children(): 
            self.tokens_table.delete(item)
        self.ast_box.delete("1.0", tk.END)
        self.semantic_box.delete("1.0", tk.END)
        self.python_box.delete("1.0", tk.END)
        self.output_box.delete("1.0", tk.END)
        self.status_lbl.configure(text="🟢 Output Cleared", text_color=self.green)

    def highlight_generated_python(self, py_code):
        py_box = self.python_box._textbox
        for tag in ["py_kw", "py_str", "py_num"]:
            py_box.tag_remove(tag, "1.0", tk.END)

        py_box.tag_config("py_kw", foreground=self.cyan)
        py_box.tag_config("py_str", foreground=self.green)
        py_box.tag_config("py_num", foreground=self.yellow)

        py_keywords = ["def", "if", "else", "elif", "while", "for", "return", "print", "in"]
        lines = py_code.split("\n")
        
        for row, line in enumerate(lines, start=1):
            for m in re.finditer(r'".*?"|\'.*?\'', line):
                py_box.tag_add("py_str", f"{row}.{m.start()}", f"{row}.{m.end()}")
            for m in re.finditer(r'\b\d+(\.\d+)?\b', line):
                py_box.tag_add("py_num", f"{row}.{m.start()}", f"{row}.{m.end()}")
            for word in py_keywords:
                for m in re.finditer(rf'\b{word}\b', line):
                    py_box.tag_add("py_kw", f"{row}.{m.start()}", f"{row}.{m.end()}")

    def run_compiler(self):
        self.clear_outputs()
        self.status_lbl.configure(text="⏳ Compiling...", text_color=self.yellow)
        self.root.update() 
        
        try:
            code = self.editor.get("1.0", tk.END)
            
            # =================================================
            # Phase 1: Tokens (WITH ROW COLORS)
            # =================================================
            tokens = tokenize(code)
            for t in tokens:
                if len(t) == 4:
                    ttype, val, ln, cl = t
                else:
                    ttype, val, ln = t
                    cl = "-"
                
                # Determine color tag based on token type
                tag = "identifier"
                if ttype in ["FUNCTION", "IF", "ELSE", "ELSE_IF", "WHILE", "FOR", "RETURN", "PRINT"]:
                    tag = "keyword"
                elif ttype in ["NUMBER", "FLOAT"]:
                    tag = "number"
                elif ttype == "STRING":
                    tag = "string"
                elif ttype == "COMMENT":
                    tag = "comment"
                elif ttype not in ["IDENTIFIER"]: 
                    # Catch-all for operators and symbols like PLUS, MINUS, LPAREN, etc.
                    tag = "operator"

                # Insert into table with the specific tag
                self.tokens_table.insert("", tk.END, values=(ln, cl, ttype, val), tags=(tag,))
            
            # Phase 2: Parser & AST
            parser = Parser(tokens)
            ast = parser.parse()
            self.ast_box.insert("1.0", self.ast_to_text(ast))
            
            # Phase 3: Semantic
            semantic_check(ast)
            self.semantic_box.insert("1.0", "✔ SEMANTIC CHECK PASSED\nNo type or scope errors found.")
            self.semantic_box.configure(text_color=self.green)
            
            # Phase 4: Code Gen
            py_code = generate_python(ast)
            self.python_box.insert("1.0", py_code)
            self.highlight_generated_python(py_code) 
            
            # Phase 5: Execute
            old_stdout = sys.stdout
            mystdout = io.StringIO()
            sys.stdout = mystdout
            exec(py_code, {"__name__": "__main__"})
            sys.stdout = old_stdout
            
            self.output_box.insert("1.0", mystdout.getvalue())
            self.output_box.configure(text_color=self.white)
            
            self.status_lbl.configure(text="🟢 Compilation Successful", text_color=self.green)
            self.tabs.set("OUTPUT") 

        except Exception as e:
            self.show_error(str(e))

    def show_error(self, error_msg):
        self.output_box.insert("1.0", f"✖ RUNTIME/COMPILER ERROR:\n\n{error_msg}")
        self.output_box.configure(text_color=self.red)
        
        self.semantic_box.insert("1.0", f"✖ ANALYSIS FAILED:\n\n{error_msg}")
        self.semantic_box.configure(text_color=self.red)
        
        self.status_lbl.configure(text="🔴 Compilation Failed", text_color=self.red)
        self.tabs.set("OUTPUT")

    def ast_to_text(self, node, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        if isinstance(node, tuple):
            text = prefix + connector + str(node[0]) + "\n"
            # =====================================================
            # SPECIAL IF FORMAT
            # =====================================================

            if node[0] == "IF":

                text = prefix + connector + "IF\n"

                branches = node[1]
                else_block = node[2]

                new_prefix = prefix + (
                    "    " if is_last else "│   "
                )

                for i, (cond, block) in enumerate(branches):

                    text += self.ast_to_text(
                        cond,
                        new_prefix,
                        False
                    )

                    text += self.ast_to_text(
                        block,
                        new_prefix,
                        True
                    )

                if else_block:

                    text += (
                        new_prefix +
                        "└── ELSE\n"
                    )

                    text += self.ast_to_text(
                        else_block,
                        new_prefix + "    ",
                        True
                    )

                return text

            children = node[1:]
            for i, child in enumerate(children):
                last = i == len(children) - 1
                text += self.ast_to_text(child, prefix + ("    " if is_last else "│   "), last)
            return text
        elif isinstance(node, list):
            text = ""
            for i, item in enumerate(node):
                text += self.ast_to_text(item, prefix, i == len(node) - 1)
            return text
        return prefix + connector + str(node) + "\n"

    def insert_tab(self, event):
        self.editor.insert("insert", "    ")
        return "break"

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    root = ctk.CTk()
    app = JungleByteIDE(root)
    root.mainloop()