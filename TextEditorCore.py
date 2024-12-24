import json
import os
import tkinter as tk

from tkinter import filedialog, font, messagebox, colorchooser
from PIL import Image, ImageTk


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Текстовый редактор")
        self.root.geometry("1500x700")
        self.root.resizable(False, False)

        self.is_fullscreen = False  # Флаг для отслеживания полноэкранного режима

        # Создание текстового виджета (но не pack)
        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True, font=("Arial", 12))

        # Панель инструментов
        self.create_toolbar()

        # Текстовый виджет
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 0))

        # Статус-бар
        self.status_bar = tk.Label(self.root, text="Строк: 1 Слов: 0 Символов: 0", anchor=tk.E)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Обновление статуса
        self.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.text_area.bind("<Control-z>", lambda event: self.undo())

        # Главное меню
        self.create_menu()

        self.history = []  # Стек для хранения истории действий
        self.redo_stack = []  # Стек для повторения отменённых действий
        self.is_restoring = False  # Флаг, чтобы избежать зацикливания

        # Сохранение действий
        self.text_area.bind("<KeyRelease>", lambda event: self.record_change(event, "text"))
        self.text_area.bind("<ButtonRelease-1>", lambda event: self.record_change(event, "format"))

        # Привязка горячих клавиш
        self.bind_shortcuts()

    def create_menu(self):
        menu = tk.Menu(self.root)

        # Меню Файл
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить как", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.confirm_exit)
        menu.add_cascade(label="Файл", menu=file_menu)

        # Меню Правка
        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Поиск", command=self.search_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Поиск и замена", command=self.find_and_replace, accelerator="Ctrl+H")
        menu.add_cascade(label="Правка", menu=edit_menu)

        # Меню Вид
        self.view_menu = tk.Menu(menu, tearoff=0)  # Сохраняем ссылку на подменю "Вид"
        self.view_menu.add_command(label="Тёмная тема", command=self.dark_mode)
        self.view_menu.add_command(label="Светлая тема", command=self.light_mode)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Полноэкранный режим", command=self.toggle_fullscreen)
        menu.add_cascade(label="Вид", menu=self.view_menu)

        # Установка меню
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

        # Загрузка иконки для цвета текста
        image = Image.open("palette.png").resize((24, 24))
        palette_icon = ImageTk.PhotoImage(image)

        # Кнопка цвета текста с иконкой
        color_button = tk.Button(toolbar, image=palette_icon, command=self.change_text_color)
        color_button.image = palette_icon  # Сохраняем ссылку на изображение
        color_button.pack(side=tk.LEFT, padx=5)

        # Разделитель
        separator = tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN, bg="gray")
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Жирный шрифт
        bold_button = tk.Button(toolbar, text="Жирный", command=self.toggle_bold)
        bold_button.pack(side=tk.LEFT, padx=5)

        # Курсив
        italic_button = tk.Button(toolbar, text="Курсив", command=self.toggle_italic)
        italic_button.pack(side=tk.LEFT, padx=5)

        # Подчёркивание
        underline_button = tk.Button(toolbar, text="Подчёркивание", command=self.toggle_underline)
        underline_button.pack(side=tk.LEFT, padx=5)

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
        """Переключает между полноэкранным и оконным режимами."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

        # Обновляем текст пункта меню
        self.view_menu.entryconfig(3, label="Оконный режим" if self.is_fullscreen else "Полноэкранный режим")

    def insert_image(self):
        """Вставляет изображение в позицию курсора."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            try:
                # Запрос ширины и высоты изображения
                width = int(self.simple_input("Введите ширину картинки:", "400"))
                height = int(self.simple_input("Введите высоту картинки:", "300"))

                # Открытие и изменение размера изображения
                image = Image.open(file_path)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(image)

                # Получаем текущую позицию курсора и вставляем изображение
                cursor_position = self.text_area.index(tk.INSERT)
                self.text_area.image_create(cursor_position, image=self.photo_image)
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
        """Открывает текстовый или JSON файл с текстом и форматированием."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            file_extension = os.path.splitext(file_path)[1].lower()
            try:
                if file_extension == ".json":
                    # Загружаем текст и форматирование из JSON
                    with open(file_path, "r", encoding="utf-8") as file:
                        json_data = json.load(file)
                        self.json_to_text(json_data)
                elif file_extension == ".txt":
                    # Загружаем текст из текстового файла
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        self.text_area.delete("1.0", tk.END)  # Очистка текстового поля
                        self.text_area.insert("1.0", content)  # Вставка текста из файла
                else:
                    messagebox.showwarning("Ошибка", "Поддерживаются только файлы формата JSON и TXT.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def text_to_json(self):
        """Конвертирует текст с форматированием в JSON, включая стиль текста, цвет, размер и шрифт."""
        data = []
        current_index = "1.0"

        while current_index != self.text_area.index(tk.END):
            try:
                # Получаем текст символа
                next_index = self.text_area.index(f"{current_index} +1c")
                char = self.text_area.get(current_index, next_index)

                # Инициализируем параметры
                font_name = "Arial"
                font_size = 12
                color = "#000000"
                bold = False
                italic = False
                underline = False

                # Извлекаем теги символа
                tags = self.text_area.tag_names(current_index)
                for tag in tags:
                    try:
                        # Извлекаем шрифт
                        font_config = self.text_area.tag_cget(tag, "font")
                        if font_config:
                            parts = font_config.split()
                            font_name = parts[0]
                            if len(parts) > 1:
                                font_size = int(parts[1])

                        # Проверяем жирность
                        if tag == "bold":
                            bold = True

                        # Проверяем курсив
                        if tag == "italic":
                            italic = True

                        # Проверяем подчёркивание
                        if tag == "underline":
                            underline = True

                        # Проверяем и извлекаем цвет текста
                        if "color" in tag:
                            color = self.text_area.tag_cget(tag, "foreground")
                    except tk.TclError as e:
                        print(f"[ERROR] Ошибка при извлечении данных из тега '{tag}': {e}")

                # Добавляем данные о символе
                data.append({
                    "text": char,  # Сохраняем даже пробелы и пустые строки
                    "font": font_name,
                    "size": font_size,
                    "bold": bold,
                    "italic": italic,
                    "underline": underline,
                    "color": color
                })

                # Обновляем текущий индекс
                current_index = next_index

            except Exception as e:
                print(f"[ERROR] Ошибка обработки символа {current_index}: {e}")
                break

        return data

    def json_to_text(self, json_data):
        """Восстанавливает текст с форматированием из JSON, включая пустые строки и пробелы."""
        self.text_area.delete(1.0, tk.END)  # Удаляем существующий текст

        for char_data in json_data:

            start_index = self.text_area.index(tk.INSERT)
            self.text_area.insert(tk.INSERT, char_data["text"])
            end_index = self.text_area.index(tk.INSERT)

            # Применяем шрифт и размер
            font_tag = f"font_{char_data['font']}_{char_data['size']}"
            self.text_area.tag_configure(font_tag, font=(char_data["font"], char_data["size"]))
            self.text_area.tag_add(font_tag, start_index, end_index)

            # Применяем жирность
            if char_data["bold"]:
                self.text_area.tag_add("bold", start_index, end_index)
                self.text_area.tag_configure("bold", font=(char_data["font"], char_data["size"], "bold"))

            # Применяем курсив
            if char_data["italic"]:
                self.text_area.tag_add("italic", start_index, end_index)
                self.text_area.tag_configure("italic", font=(char_data["font"], char_data["size"], "italic"))

            # Применяем подчёркивание
            if char_data["underline"]:
                self.text_area.tag_add("underline", start_index, end_index)
                self.text_area.tag_configure("underline", underline=True)

            # Применяем цвет текста
            if char_data["color"]:
                color_tag = f"color_{char_data['color']}"
                self.text_area.tag_configure(color_tag, foreground=char_data["color"])
                self.text_area.tag_add(color_tag, start_index, end_index)

    def save_file(self):
        """Сохраняет текст в текстовый файл или файл с форматированием в JSON."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")]
        )
        if file_path:
            file_extension = os.path.splitext(file_path)[1].lower()
            try:
                if file_extension == ".json":
                    # Сохраняем текст и форматирование в JSON
                    with open(file_path, "w", encoding="utf-8") as file:
                        json_data = self.text_to_json()
                        json.dump(json_data, file, ensure_ascii=False, indent=4)
                    messagebox.showinfo("Сохранение", "Файл успешно сохранён в формате JSON!")
                elif file_extension == ".txt":
                    # Сохраняем текст в текстовый файл
                    with open(file_path, "w", encoding="utf-8") as file:
                        content = self.text_area.get("1.0", tk.END).strip()  # Получаем текст из текстового поля
                        file.write(content)
                    messagebox.showinfo("Сохранение", "Файл успешно сохранён в формате TXT!")
                else:
                    messagebox.showwarning("Ошибка", "Поддерживаются только файлы формата JSON и TXT.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

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
        """Изменяет цвет выделенного текста."""
        color = colorchooser.askcolor()[1]  # Выбираем цвет
        if color:
            try:
                start_index = self.text_area.index(tk.SEL_FIRST)
                end_index = self.text_area.index(tk.SEL_LAST)
                color_tag = f"color_{color}"

                # Настраиваем и добавляем тег цвета
                self.text_area.tag_configure(color_tag, foreground=color)
                self.text_area.tag_add(color_tag, start_index, end_index)

                # Сохраняем изменение в историю
                self.record_change(change_type="format")
            except tk.TclError:
                messagebox.showwarning("Ошибка", "Выделите текст для изменения цвета.")

    def toggle_bold(self):
        """Добавляет или убирает жирный шрифт."""
        try:
            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            if "bold" in self.text_area.tag_names(start_index):
                self.text_area.tag_remove("bold", start_index, end_index)
            else:
                self.text_area.tag_add("bold", start_index, end_index)
                self.text_area.tag_configure("bold", font=(self.font_var.get(), self.size_var.get(), "bold"))
        except tk.TclError:
            messagebox.showwarning("Ошибка", "Выделите текст для применения жирного шрифта.")

    def toggle_italic(self):
        """Добавляет или убирает курсив."""
        try:
            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            if "italic" in self.text_area.tag_names(start_index):
                self.text_area.tag_remove("italic", start_index, end_index)
            else:
                self.text_area.tag_add("italic", start_index, end_index)
                self.text_area.tag_configure("italic", font=(self.font_var.get(), self.size_var.get(), "italic"))
        except tk.TclError:
            messagebox.showwarning("Ошибка", "Выделите текст для применения курсива.")

    def toggle_underline(self):
        """Добавляет или убирает подчёркивание."""
        try:
            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            if "underline" in self.text_area.tag_names(start_index):
                self.text_area.tag_remove("underline", start_index, end_index)
            else:
                self.text_area.tag_add("underline", start_index, end_index)
                self.text_area.tag_configure("underline", underline=True)
        except tk.TclError:
            messagebox.showwarning("Ошибка", "Выделите текст для применения подчёркивания.")

    def update_status_bar(self, event=None):
        cursor_position = self.text_area.index(tk.INSERT)
        row, col = map(int, cursor_position.split('.'))
        text_content = self.text_area.get(1.0, tk.END)
        num_chars = len(text_content) - 1
        num_words = len(text_content.split())
        self.status_bar.config(
            text=f"Строка: {row} | Столбец: {col} | Слов: {num_words} | Символов: {num_chars}"
        )

    def record_change(self, event=None, change_type="text"):
        """Сохраняет изменения текста или форматирования в историю."""
        if self.is_restoring:
            return

        action = None

        if change_type == "text":
            current_text = self.text_area.get(1.0, tk.END).strip()
            cursor_position = self.text_area.index(tk.INSERT)

            if self.history and self.history[-1]["type"] == "text" and self.history[-1]["text"] == current_text:
                return

            action = {
                "type": "text",
                "text": current_text,
                "cursor": cursor_position,
            }

        elif change_type == "format":
            if not self.text_area.tag_ranges(tk.SEL):
                return

            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            tags = self.text_area.tag_names(start_index)

            # Извлекаем шрифт, размер и атрибуты
            font = self.get_font_from_tags(tags)
            size = self.get_font_size_from_tags(tags)
            bold = "bold" in tags
            italic = "italic" in tags
            underline = "underline" in tags
            color = self.get_color_from_tags(tags)

            action = {
                "type": "format",
                "start": start_index,
                "end": end_index,
                "tags": tags,
                "font": font,
                "size": size,
                "bold": bold,
                "italic": italic,
                "underline": underline,
                "color": color,
            }

        if action:
            self.history.append(action)
            self.redo_stack.clear()

    def get_font_from_tags(self, tags):
        """Возвращает шрифт из списка тегов."""
        for tag in tags:
            try:
                font_config = self.text_area.tag_cget(tag, "font")
                if font_config:
                    return font_config.split()[0]
            except tk.TclError:
                continue
        return "Arial"

    def get_font_size_from_tags(self, tags):
        """Возвращает размер шрифта из списка тегов."""
        for tag in tags:
            try:
                font_config = self.text_area.tag_cget(tag, "font")
                if font_config and len(font_config.split()) > 1:
                    return int(font_config.split()[1])
            except tk.TclError:
                continue
        return 12

    def get_color_from_tags(self, tags):
        """Возвращает цвет из списка тегов."""
        for tag in tags:
            try:
                if tag.startswith("color_"):
                    return self.text_area.tag_cget(tag, "foreground")
            except tk.TclError:
                continue
        return "#000000"

    def get_affected_range(self, cursor_position, tags):
        """Возвращает диапазон текста, затронутого изменением."""
        start_index = cursor_position
        end_index = f"{cursor_position} +1c"

        for tag in tags:
            ranges = self.text_area.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                if self.text_area.compare(cursor_position, ">=", ranges[i]) and self.text_area.compare(cursor_position,
                                                                                                       "<",
                                                                                                       ranges[i + 1]):
                    start_index = ranges[i]
                    end_index = ranges[i + 1]
                    break

        return start_index, end_index

    def undo(self):
        """Отменяет последнее действие."""
        if not self.history:
            messagebox.showinfo("Отмена", "Нет действий для отмены.")
            return

        last_action = self.history.pop()
        self.is_restoring = True
        try:
            if last_action["type"] == "text":
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, last_action["text"])
                self.text_area.mark_set(tk.INSERT, last_action["cursor"])
            elif last_action["type"] == "format":
                start = last_action["start"]
                end = last_action["end"]
                for tag in last_action["tags"]:
                    self.text_area.tag_remove(tag, start, end)

                # Восстановление шрифта и размера
                font_tag = f"font_{last_action['font']}_{last_action['size']}"
                self.text_area.tag_configure(font_tag, font=(last_action["font"], last_action["size"]))
                self.text_area.tag_add(font_tag, start, end)

                # Восстановление других атрибутов
                if last_action["bold"]:
                    self.text_area.tag_add("bold", start, end)

                if last_action["italic"]:
                    self.text_area.tag_add("italic", start, end)

                if last_action["underline"]:
                    self.text_area.tag_add("underline", start, end)

                if last_action["color"]:
                    color_tag = f"color_{last_action['color']}"
                    self.text_area.tag_configure(color_tag, foreground=last_action["color"])
                    self.text_area.tag_add(color_tag, start, end)

            self.redo_stack.append(last_action)
        except Exception as e:
            print(f"[ERROR] Ошибка в undo: {e}")
        finally:
            self.is_restoring = False

    def redo(self):
        """Повторяет последнее отменённое действие."""
        if not self.redo_stack:
            messagebox.showinfo("Повтор", "Нет действий для повторения.")
            return

        last_action = self.redo_stack.pop()
        self.is_restoring = True
        try:
            if last_action["type"] == "text":
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, last_action["text"])
                self.text_area.mark_set(tk.INSERT, last_action["cursor"])
            elif last_action["type"] == "format":
                start = last_action["start"]
                end = last_action["end"]

                # Повторение шрифта и размера
                font_tag = f"font_{last_action['font']}_{last_action['size']}"
                self.text_area.tag_configure(font_tag, font=(last_action["font"], last_action["size"]))
                self.text_area.tag_add(font_tag, start, end)

                # Повторение других атрибутов
                if last_action["bold"]:
                    self.text_area.tag_add("bold", start, end)

                if last_action["italic"]:
                    self.text_area.tag_add("italic", start, end)

                if last_action["underline"]:
                    self.text_area.tag_add("underline", start, end)

                if last_action["color"]:
                    color_tag = f"color_{last_action['color']}"
                    self.text_area.tag_configure(color_tag, foreground=last_action["color"])
                    self.text_area.tag_add(color_tag, start, end)

            self.history.append(last_action)
        except Exception as e:
            print(f"[ERROR] Ошибка в redo: {e}")
        finally:
            self.is_restoring = False

    def confirm_exit(self):
        """Запрос подтверждения выхода из программы."""
        if messagebox.askyesno("Подтверждение выхода", "Вы действительно хотите выйти?"):
            self.root.quit()

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", self.open_file)
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-f>", self.search_text)
        self.root.bind("<Control-r>", self.find_and_replace)
        self.root.bind("<Control-q>", self.confirm_exit)


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
