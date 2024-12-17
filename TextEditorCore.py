import tkinter as tk
from tkinter import filedialog, font, messagebox, colorchooser


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Текстовый редактор")
        self.root.geometry("800x600")  # Установка фиксированного размера
        self.root.resizable(False, False)  # Запрет изменения размеров окна

        # Панель инструментов (закреплена сверху)
        self.create_toolbar()

        # Текстовая область
        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True, font=("Arial", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 0))

        # Статус-бар (закреплён снизу)
        self.status_bar = tk.Label(self.root, text="Строк: 1 Слов: 0 Символов: 0", anchor=tk.E)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Обновление статуса при вводе текста
        self.text_area.bind("<KeyRelease>", self.update_status_bar)

        # Главное меню
        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить как", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menu.add_cascade(label="Файл", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Поиск", command=self.search_text)
        edit_menu.add_command(label="Поиск и замена", command=self.find_and_replace)
        menu.add_cascade(label="Правка", menu=edit_menu)

        view_menu = tk.Menu(menu, tearoff=0)
        view_menu.add_command(label="Тёмная тема", command=self.dark_mode)
        view_menu.add_command(label="Светлая тема", command=self.light_mode)
        menu.add_cascade(label="Вид", menu=view_menu)

        self.root.config(menu=menu)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#f0f0f0")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Font Selector
        font_list = list(font.families())
        self.font_var = tk.StringVar(value="Arial")
        font_menu = tk.OptionMenu(toolbar, self.font_var, *font_list, command=self.change_font)
        font_menu.pack(side=tk.LEFT, padx=5)

        # Font Size
        self.size_var = tk.IntVar(value=12)
        size_menu = tk.Spinbox(toolbar, from_=8, to=72, textvariable=self.size_var, command=self.change_font)
        size_menu.pack(side=tk.LEFT, padx=5)

        # Text Color
        color_button = tk.Button(toolbar, text="Цвет текста", command=self.change_text_color)
        color_button.pack(side=tk.LEFT, padx=5)

        # Line Spacing
        spacing_label = tk.Label(toolbar, text="Межстрочный интервал:")
        spacing_label.pack(side=tk.LEFT, padx=5)

        self.spacing_var = tk.DoubleVar(value=1.5)
        spacing_menu = tk.Spinbox(toolbar, from_=1.0, to=3.0, increment=0.1, textvariable=self.spacing_var,
                                  command=self.change_line_spacing)
        spacing_menu.pack(side=tk.LEFT, padx=5)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Rich Text Format", "*.rtf"), ("Markdown", "*.md")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("Rich Text Format", "*.rtf"),
                                                            ("Markdown", "*.md")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END))

    def change_font(self, *args):
        current_font = self.font_var.get()
        current_size = self.size_var.get()
        self.text_area.configure(font=(current_font, current_size))

    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text_area.configure(fg=color)

    def change_line_spacing(self):
        spacing = self.spacing_var.get()
        self.text_area.configure(spacing1=spacing, spacing3=spacing)

    def dark_mode(self):
        self.text_area.configure(bg="#2E2E2E", fg="white", insertbackground="white")
        self.status_bar.configure(bg="#2E2E2E", fg="white")

    def light_mode(self):
        self.text_area.configure(bg="white", fg="black", insertbackground="black")
        self.status_bar.configure(bg="white", fg="black")

    def search_text(self):
        messagebox.showinfo("Поиск", "Функция поиска!")

    def find_and_replace(self):
        messagebox.showinfo("Поиск и замена", "Функция поиска и замены!")

    def update_status_bar(self, event=None):
        text_content = self.text_area.get(1.0, tk.END)
        num_chars = len(text_content) - 1
        num_words = len(text_content.split())
        num_lines = text_content.count("\n")
        self.status_bar.config(text=f"Строк: {num_lines} Слов: {num_words} Символов: {num_chars}")


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
