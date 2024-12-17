import tkinter as tk
from tkinter import filedialog, font, messagebox, colorchooser
from PIL import Image, ImageTk
from PIL.Image import Resampling


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Текстовый редактор")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.is_fullscreen = False  # Флаг для отслеживания полноэкранного режима

        # Панель инструментов
        self.create_toolbar()

        # Текстовая область
        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True, font=("Arial", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 0))

        # Статус-бар
        self.status_bar = tk.Label(self.root, text="Строк: 1 Слов: 0 Символов: 0", anchor=tk.E)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Обновление статуса
        self.text_area.bind("<KeyRelease>", self.update_status_bar)

        # Главное меню
        self.create_menu()

        self.bind_shortcuts()

    def create_menu(self):
        menu = tk.Menu(self.root)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить как", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.confirm_exit)
        menu.add_cascade(label="Файл", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Поиск", command=self.search_text)
        edit_menu.add_command(label="Поиск и замена", command=self.find_and_replace)
        menu.add_cascade(label="Правка", menu=edit_menu)

        view_menu = tk.Menu(menu, tearoff=0)
        view_menu.add_command(label="Тёмная тема", command=self.dark_mode)
        view_menu.add_command(label="Светлая тема", command=self.light_mode)
        view_menu.add_separator()
        view_menu.add_command(label="Полноэкранный режим", command=self.toggle_fullscreen)
        menu.add_cascade(label="Вид", menu=view_menu)

        self.root.config(menu=menu)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#f0f0f0")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Шрифт
        tk.Label(toolbar, text="Шрифт:").pack(side=tk.LEFT, padx=5)
        font_list = list(font.families())
        self.font_var = tk.StringVar(value="Arial")
        font_menu = tk.OptionMenu(toolbar, self.font_var, *font_list)
        font_menu.pack(side=tk.LEFT, padx=5)

        # Разделитель
        separator = tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN, bg="gray")
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Размер шрифта
        tk.Label(toolbar, text="Размер:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=12)
        size_entry = tk.Spinbox(toolbar, from_=8, to=72, textvariable=self.size_var)
        size_entry.pack(side=tk.LEFT, padx=5)

        # Разделитель
        separator = tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN, bg="gray")
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Цвет текста
        color_button = tk.Button(toolbar, text="Цвет текста", command=self.change_text_color)
        color_button.pack(side=tk.LEFT, padx=5)

        # Разделитель
        separator = tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN, bg="gray")
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Кнопка применения шрифта
        font_button = tk.Button(toolbar, text="Применить шрифт", command=self.change_font)
        font_button.pack(side=tk.LEFT, padx=5)

        # Разделитель
        separator = tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN, bg="gray")
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Вставка изображения
        insert_image_button = tk.Button(toolbar, text="Вставить картинку", command=self.insert_image)
        insert_image_button.pack(side=tk.LEFT, padx=5)

    def dark_mode(self):
        """Темная тема оформления."""
        self.root.configure(bg="#2B2B2B")
        self.text_area.configure(bg="#2B2B2B", fg="#E0E0E0", insertbackground="white")
        self.status_bar.configure(bg="#2B2B2B", fg="#E0E0E0")

    def light_mode(self):
        """Светлая тема оформления."""
        self.root.configure(bg="white")
        self.text_area.configure(bg="white", fg="black", insertbackground="black")
        self.status_bar.configure(bg="white", fg="black")

    def toggle_fullscreen(self):
        """Включает/выключает полноэкранный режим."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def insert_image(self):
        """Открывает диалог для вставки изображения и изменения его размера."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            try:
                # Запрос ширины и высоты у пользователя
                width = int(self.simple_input("Введите ширину картинки:", "400"))
                height = int(self.simple_input("Введите высоту картинки:", "300"))

                # Открытие и изменение размера изображения
                image = Image.open(file_path)
                image = image.resize((width, height), Resampling.LANCZOS)  # Заменено на Resampling.LANCZOS
                self.photo_image = ImageTk.PhotoImage(image)

                # Вставка изображения
                self.text_area.image_create(tk.END, image=self.photo_image)
                self.text_area.insert(tk.END, "\n")  # Добавляем перенос строки
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось вставить изображение: {e}")

    def simple_input(self, prompt, default_value=""):
        """Запрашивает ввод у пользователя через окно."""
        input_window = tk.Toplevel(self.root)
        input_window.title("Ввод значения")
        tk.Label(input_window, text=prompt).pack(padx=10, pady=5)
        input_var = tk.StringVar(value=default_value)
        input_entry = tk.Entry(input_window, textvariable=input_var)
        input_entry.pack(padx=10, pady=5)
        input_entry.focus()

        def confirm():
            input_window.destroy()

        tk.Button(input_window, text="OK", command=confirm).pack(pady=5)
        input_window.wait_window()
        return input_var.get()

    def search_text(self):
        """Осуществляет поиск текста и подсвечивает найденные фрагменты."""

        def find():
            # Удаляем старое выделение
            self.text_area.tag_remove("highlight", "1.0", tk.END)
            search_query = search_entry.get()

            if search_query:
                start_pos = "1.0"
                while True:
                    # Ищем текст в тексте
                    start_pos = self.text_area.search(search_query, start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(search_query)}c"
                    self.text_area.tag_add("highlight", start_pos, end_pos)
                    start_pos = end_pos

                # Настройка тега для подсветки
                self.text_area.tag_configure("highlight", background="yellow", foreground="black")

        # Создаём диалоговое окно для поиска
        search_window = tk.Toplevel(self.root)
        search_window.title("Поиск")
        search_window.geometry("300x100")
        search_window.transient(self.root)
        search_window.resizable(False, False)

        tk.Label(search_window, text="Введите текст для поиска:").pack(pady=5)
        search_entry = tk.Entry(search_window, width=30)
        search_entry.pack(pady=5)

        find_button = tk.Button(search_window, text="Найти", command=find)
        find_button.pack(pady=5)

    def find_and_replace(self):
        """Осуществляет поиск и замену текста."""

        def replace():
            search_query = search_entry.get()
            replace_query = replace_entry.get()

            if search_query:
                content = self.text_area.get("1.0", tk.END)
                new_content = content.replace(search_query, replace_query)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", new_content)

                messagebox.showinfo("Завершено", f"Все вхождения '{search_query}' заменены на '{replace_query}'.")

        # Создаём диалоговое окно для поиска и замены
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Поиск и замена")
        replace_window.geometry("350x150")
        replace_window.transient(self.root)
        replace_window.resizable(False, False)

        tk.Label(replace_window, text="Найти:").pack(pady=5)
        search_entry = tk.Entry(replace_window, width=30)
        search_entry.pack(pady=5)

        tk.Label(replace_window, text="Заменить на:").pack(pady=5)
        replace_entry = tk.Entry(replace_window, width=30)
        replace_entry.pack(pady=5)

        replace_button = tk.Button(replace_window, text="Заменить", command=replace)
        replace_button.pack(pady=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END))

    def change_font(self):
        font_name = self.font_var.get()
        font_size = self.size_var.get()
        try:
            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            font_tag = f"font_{font_name}_{font_size}"
            self.text_area.tag_configure(font_tag, font=(font_name, font_size))
            self.text_area.tag_add(font_tag, start_index, end_index)
        except tk.TclError:
            messagebox.showwarning("Ошибка", "Выделите текст для изменения шрифта.")

    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            try:
                start_index = self.text_area.index(tk.SEL_FIRST)
                end_index = self.text_area.index(tk.SEL_LAST)
                color_tag = f"color_{color}"
                self.text_area.tag_configure(color_tag, foreground=color)
                self.text_area.tag_add(color_tag, start_index, end_index)
            except tk.TclError:
                messagebox.showwarning("Ошибка", "Выделите текст для изменения цвета.")

    def update_status_bar(self, event=None):
        cursor_position = self.text_area.index(tk.INSERT)
        row, col = map(int, cursor_position.split('.'))
        text_content = self.text_area.get(1.0, tk.END)
        num_chars = len(text_content) - 1
        num_words = len(text_content.split())
        num_lines = text_content.count("\n")
        self.status_bar.config(
            text=f"Строка: {row} | Столбец: {col} | Строк: {num_lines} | Слов: {num_words} | Символов: {num_chars}"
        )

    def confirm_exit(self):
        """Запрос подтверждения выхода из программы."""
        if messagebox.askyesno("Подтверждение выхода", "Вы действительно хотите выйти?"):
            self.root.quit()

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-f>", lambda event: self.search_text())
        self.root.bind("<Control-r>", lambda event: self.find_and_replace())
        self.root.bind("<Control-q>", lambda event: self.confirm_exit())


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
