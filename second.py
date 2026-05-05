import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font, colorchooser
import os
import subprocess
import tempfile

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad 11.2508.38.0")
        self.root.geometry("1000x700")
        
        # Variables
        self.current_zoom = 100
        self.word_wrap_var = tk.BooleanVar(value=True)
        self.tabs = []  
        
        self.setup_ui()
        self.create_new_tab()  
    
    def setup_ui(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.create_new_tab)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Search...", accelerator="Ctrl+F", command=self.search_word)
        edit_menu.add_command(label="Replace...", accelerator="Ctrl+H", command=self.replace_word)
        
        # Format Menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Font...", command=self.change_font)
        format_menu.add_command(label="Text Color...", command=self.change_text_color)
        format_menu.add_command(label="Background Color...", command=self.change_bg_color)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", accelerator="Ctrl++", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", accelerator="Ctrl+-", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        view_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap_var, command=self.toggle_word_wrap)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Word Count", command=self.show_word_count)
        tools_menu.add_command(label="Auto Completion", command=self.show_autocomplete)
        tools_menu.add_command(label="Run Python Code", command=self.run_python_code)
        tools_menu.add_command(label="Drawing Tool", command=self.open_drawing_tool)
        
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        ttk.Button(toolbar, text="New", width=6, command=self.create_new_tab).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open", width=6, command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", width=6, command=self.save_file).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        
        ttk.Button(toolbar, text="🔍 Search", command=self.search_word).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🎨 Draw", command=self.open_drawing_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Zoom+", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Zoom-", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        
        # Tabbed Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # Status Bar
        self.status_bar = tk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.Label(self.status_bar, text="Ln 1, Col 1    |    100%    |    Word Wrap: On", anchor=tk.W)
        self.status_text.pack(side=tk.LEFT, padx=10, pady=2)
        
        self.length_label = tk.Label(self.status_bar, text="Length: 0")
        self.length_label.pack(side=tk.RIGHT, padx=10)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.create_new_tab())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-f>", lambda e: self.search_word())
        self.root.bind("<Control-h>", lambda e: self.replace_word())
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
    
    # ====================== UNDO & REDO ======================
    def undo(self):
        tab = self.get_current_tab()
        if tab:
            try:
                tab['text_widget'].edit_undo()
            except:
                pass
    
    def redo(self):
        tab = self.get_current_tab()
        if tab:
            try:
                tab['text_widget'].edit_redo()
            except:
                pass
    
    # ====================== CORE TAB METHODS ======================
    def create_new_tab(self, title="Untitled"):
        frame = ttk.Frame(self.notebook)
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD if self.word_wrap_var.get() else tk.NONE,
            undo=True,
            font=("Consolas", 11)
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.bind("<KeyRelease>", lambda e: self.update_status(text_widget))
        text_widget.bind("<Button-1>", lambda e: self.update_status(text_widget))
        
        self.notebook.add(frame, text=title)
        self.notebook.select(frame)
        
        self.tabs.append({
            'frame': frame,
            'text_widget': text_widget,
            'filename': None,
            'modified': False
        })
        self.update_status(text_widget)
        return text_widget
    
    def get_current_tab(self):
        if not self.tabs:
            return None
        current_index = self.notebook.index("current")
        return self.tabs[current_index]
    
    def on_tab_change(self, event=None):
        tab = self.get_current_tab()
        if tab:
            self.update_status(tab['text_widget'])
    
    def update_status(self, text_widget):
        try:
            line, col = text_widget.index(tk.INSERT).split('.')
            content = text_widget.get("1.0", tk.END)
            length = len(content) - 1
            zoom_str = f"{self.current_zoom}%"
            wrap_str = "On" if self.word_wrap_var.get() else "Off"
            self.status_text.config(
                text=f"Ln {line}, Col {int(col)+1}    |    {zoom_str}    |    Word Wrap: {wrap_str}"
            )
            self.length_label.config(text=f"Length: {length}")
        except:
            pass
    
    # ====================== FILE OPERATIONS ======================
    def save_file(self):
        tab = self.get_current_tab()
        if not tab: return
        if not tab['filename']:
            return self.save_as_file()
        try:
            with open(tab['filename'], "w", encoding="utf-8") as f:
                f.write(tab['text_widget'].get("1.0", tk.END))
            tab['modified'] = False
            self.update_tab_title()
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
    
    def save_as_file(self):
        tab = self.get_current_tab()
        if not tab: return
        file = filedialog.asksaveasfilename(defaultextension=".txt", 
                                          filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file:
            try:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(tab['text_widget'].get("1.0", tk.END))
                tab['filename'] = file
                tab['modified'] = False
                self.update_tab_title()
            except Exception as e:
                messagebox.showerror("Save Error", str(e))
    
    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                new_tab = self.create_new_tab(os.path.basename(file))
                new_tab.delete("1.0", tk.END)
                new_tab.insert("1.0", content)
                current_tab = self.get_current_tab()
                current_tab['filename'] = file
                current_tab['modified'] = False
                self.update_tab_title()
            except Exception as e:
                messagebox.showerror("Open Error", str(e))
    
    def update_tab_title(self):
        tab = self.get_current_tab()
        if not tab: return
        index = self.notebook.index("current")
        title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
        if tab['modified']: title = "* " + title
        self.notebook.tab(index, text=title)
    
    # ====================== TEXT FORMATTING ======================
    def change_font(self):
        tab = self.get_current_tab()
        if not tab: return
        
        font_win = tk.Toplevel(self.root)
        font_win.title("Font")
        font_win.geometry("350x250")
        font_win.resizable(False, False)
        
        families = ["Arial", "Times New Roman", "Courier New", "Calibri", "Consolas"]
        sizes = list(range(8, 37))
        
        current_font = tab['text_widget'].cget("font").split()
        current_family = current_font[0] if current_font else "Consolas"
        current_size = int(current_font[1]) if len(current_font) > 1 else 11
        
        tk.Label(font_win, text="Font Family:", font=("Arial", 10, "bold")).pack(pady=(15,5), anchor="w", padx=20)
        family_var = tk.StringVar(value=current_family)
        family_combo = ttk.Combobox(font_win, textvariable=family_var, values=families, width=30)
        family_combo.pack(pady=5, padx=20)
        
        tk.Label(font_win, text="Font Size:", font=("Arial", 10, "bold")).pack(pady=(15,5), anchor="w", padx=20)
        size_var = tk.IntVar(value=current_size)
        size_combo = ttk.Combobox(font_win, textvariable=size_var, values=sizes, width=30)
        size_combo.pack(pady=5, padx=20)
        
        def apply_font():
            try:
                new_font = (family_var.get(), size_var.get())
                tab['text_widget'].config(font=new_font)
            except:
                pass
            font_win.destroy()
        
        ttk.Button(font_win, text="Apply", command=apply_font).pack(pady=20)
    
    # ====================== OTHER METHODS (unchanged) ======================
    def show_autocomplete(self):
        tab = self.get_current_tab()
        if not tab: return
        # ... (your existing autocomplete code)
        ac_win = tk.Toplevel(self.root)
        ac_win.title("Auto Completion")
        ac_win.geometry("300x400")
        ac_win.resizable(False, False)
        
        keywords = ["if", "else", "elif", "for", "while", "def", "return", 
                    "import", "from", "class", "try", "except", "finally",
                    "print", "input", "len", "range", "True", "False", "None"]
        
        tk.Label(ac_win, text="Click to insert keyword:", font=("Arial", 11, "bold")).pack(pady=10)
        listbox = tk.Listbox(ac_win, font=("Consolas", 11), height=15)
        listbox.pack(padx=20, fill=tk.BOTH, expand=True)
        
        for kw in keywords:
            listbox.insert(tk.END, kw)
        
        def insert_keyword(event=None):
            selection = listbox.curselection()
            if selection:
                keyword = listbox.get(selection[0])
                tab['text_widget'].insert(tk.INSERT, keyword)
                ac_win.destroy()
        
        listbox.bind("<Double-Button-1>", insert_keyword)
        ttk.Button(ac_win, text="Insert", command=insert_keyword).pack(pady=10)

    def run_python_code(self):
        # ... your existing run python code (unchanged)
        tab = self.get_current_tab()
        if not tab: return
        code = tab['text_widget'].get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Empty", "No code to run!")
            return
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            result = subprocess.run(['python', tmp_path], capture_output=True, text=True, timeout=10)
            output_win = tk.Toplevel(self.root)
            output_win.title("Python Output")
            output_win.geometry("700x500")
            output_text = tk.Text(output_win, font=("Consolas", 10))
            output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            output_text.insert(tk.END, "=== STDOUT ===\n" + result.stdout)
            if result.stderr:
                output_text.insert(tk.END, "\n=== STDERR ===\n" + result.stderr)
            os.unlink(tmp_path)
        except Exception as e:
            messagebox.showerror("Run Error", str(e))

    def search_word(self):
        # ... your existing search code (kept same)
        tab = self.get_current_tab()
        if not tab: return
        text_widget = tab['text_widget']
        search_win = tk.Toplevel(self.root)
        search_win.title("Find")
        search_win.geometry("420x160")
        search_win.resizable(False, False)
        
        tk.Label(search_win, text="Find what:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=(15,5))
        search_entry = tk.Entry(search_win, width=50, font=("Arial", 10))
        search_entry.pack(padx=20, pady=5)
        search_entry.focus()
        
        def find_next():
            text_widget.tag_remove("sel", "1.0", tk.END)
            search_text = search_entry.get().strip()
            if not search_text: return
            start_pos = text_widget.search(search_text, tk.INSERT, tk.END, nocase=True)
            if not start_pos:
                start_pos = text_widget.search(search_text, "1.0", tk.END, nocase=True)
            if start_pos:
                end_pos = f"{start_pos}+{len(search_text)}c"
                text_widget.tag_add("sel", start_pos, end_pos)
                text_widget.mark_set(tk.INSERT, end_pos)
                text_widget.see(start_pos)
            else:
                messagebox.showinfo("Search Result", f"Cannot find '{search_text}'")
        
        btn_frame = ttk.Frame(search_win)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Find Next", command=find_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=search_win.destroy).pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: find_next())

    def replace_word(self):
        # ... your existing replace code
        tab = self.get_current_tab()
        if not tab: return
        replace_win = tk.Toplevel(self.root)
        replace_win.title("Find and Replace")
        replace_win.geometry("450x220")
        replace_win.resizable(False, False)
        
        tk.Label(replace_win, text="Find what:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        find_entry = tk.Entry(replace_win, width=40)
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        find_entry.focus()
        
        tk.Label(replace_win, text="Replace with:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        replace_entry = tk.Entry(replace_win, width=40)
        replace_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def replace_all():
            text_widget = tab['text_widget']
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if not find_text: return
            content = text_widget.get("1.0", tk.END)
            new_content = content.replace(find_text, replace_text)
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", new_content)
            messagebox.showinfo("Replace", f"Replaced all occurrences of '{find_text}'")
            replace_win.destroy()
        
        ttk.Button(replace_win, text="Replace All", command=replace_all).grid(row=2, column=1, pady=15)

    def change_text_color(self):
        tab = self.get_current_tab()
        if not tab: return
        color = colorchooser.askcolor(title="Text Color")
        if color[1]:
            tab['text_widget'].config(fg=color[1])
    
    def change_bg_color(self):
        tab = self.get_current_tab()
        if not tab: return
        color = colorchooser.askcolor(title="Background Color")
        if color[1]:
            tab['text_widget'].config(bg=color[1])
    
    def zoom_in(self):
        self.current_zoom = min(300, self.current_zoom + 10)
        self.apply_zoom()
    
    def zoom_out(self):
        self.current_zoom = max(30, self.current_zoom - 10)
        self.apply_zoom()
    
    def reset_zoom(self):
        self.current_zoom = 100
        self.apply_zoom()
    
    def apply_zoom(self):
        tab = self.get_current_tab()
        if not tab: return
        try:
            family = tab['text_widget'].cget("font").split()[0]
            new_size = int(11 * self.current_zoom / 100)
            tab['text_widget'].config(font=(family, new_size))
        except:
            tab['text_widget'].config(font=("Consolas", int(11 * self.current_zoom / 100)))
        self.update_status(tab['text_widget'])
    
    def toggle_word_wrap(self):
        tab = self.get_current_tab()
        if not tab: return
        wrap = tk.WORD if self.word_wrap_var.get() else tk.NONE
        tab['text_widget'].config(wrap=wrap)
    
    def show_word_count(self):
        tab = self.get_current_tab()
        if not tab: return
        content = tab['text_widget'].get("1.0", tk.END).strip()
        words = len(content.split())
        chars = len(content)
        messagebox.showinfo("Statistics", f"Words: {words}\nCharacters: {chars}")
    
    def open_drawing_tool(self):
        # ... your existing drawing tool code (unchanged)
        draw_win = tk.Toplevel(self.root)
        draw_win.title("Notepad - Drawing Tool")
        draw_win.geometry("900x700")
        canvas = tk.Canvas(draw_win, bg="white", width=800, height=550)
        canvas.pack(pady=10)
        
        last_x, last_y = None, None
        draw_color = tk.StringVar(value="black")
        
        def paint(event):
            nonlocal last_x, last_y
            x, y = event.x, event.y
            if last_x and last_y:
                canvas.create_line(last_x, last_y, x, y, width=3, fill=draw_color.get(), capstyle=tk.ROUND, smooth=True)
            last_x, last_y = x, y
        
        def reset_last_pos(event=None):
            nonlocal last_x, last_y
            last_x, last_y = None, None
        
        canvas.bind("<B1-Motion>", paint)
        canvas.bind("<ButtonRelease-1>", reset_last_pos)
        
        control_frame = ttk.Frame(draw_win)
        control_frame.pack(pady=5)
        ttk.Label(control_frame, text="Color:").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Pick Color", 
                  command=lambda: draw_color.set(colorchooser.askcolor()[1] or "black")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear", command=lambda: canvas.delete("all")).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Close", command=draw_win.destroy).pack(side=tk.RIGHT, padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadApp(root)
    root.mainloop()