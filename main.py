import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class QuoteGenerator:
    def __init__(self, window):
        self.window = window
        self.window.title("Random Quote Generator")
        self.window.geometry("800x600")
        
        # Предопределенные цитаты
        self.default_quotes = [
            {"text": "Будьте собой, все остальные роли уже заняты.", "author": "Оскар Уайльд", "theme": "Жизнь"},
            {"text": "Успех — это способность переходить от одной неудачи к другой, не теряя энтузиазма.", "author": "Уинстон Черчилль", "theme": "Успех"},
            {"text": "Самое главное — это коснуться души человека.", "author": "Антуан де Сент-Экзюпери", "theme": "Мудрость"},
            {"text": "Неважно, как медленно вы идете, пока вы не останавливаетесь.", "author": "Конфуций", "theme": "Мотивация"},
            {"text": "Лучшее время, чтобы посадить дерево, было 20 лет назад. Второе лучшее время — сегодня.", "author": "Китайская пословица", "theme": "Время"},
            {"text": "Цель без плана — это просто желание.", "author": "Антуан де Сент-Экзюпери", "theme": "Успех"},
            {"text": "Жизнь — это то, что происходит с вами, пока вы заняты другими делами.", "author": "Джон Леннон", "theme": "Жизнь"},
            {"text": "Счастье не в том, чтобы делать всегда, что хочешь, а в том, чтобы всегда хотеть того, что делаешь.", "author": "Лев Толстой", "theme": "Счастье"}
        ]
        
        # Загрузка истории из JSON
        self.history_file = "quotes.json"
        self.history = []
        self.load_history()
        
        # Создание GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Кнопка генерации
        ttk.Button(main_frame, text="Сгенерировать цитату", 
                  command=self.generate_quote).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Отображение цитаты
        self.quote_frame = ttk.LabelFrame(main_frame, text="Случайная цитата", padding="10")
        self.quote_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.quote_text = tk.Text(self.quote_frame, height=5, width=60, wrap=tk.WORD, state="disabled")
        self.quote_text.grid(row=0, column=0, columnspan=2)
        
        # Секция добавления цитаты
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую цитату", padding="10")
        add_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(add_frame, text="Текст цитаты:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_quote_text = tk.Text(add_frame, height=3, width=50)
        self.new_quote_text.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(add_frame, text="Автор:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.new_author = ttk.Entry(add_frame, width=30)
        self.new_author.grid(row=2, column=1, pady=5)
        
        ttk.Label(add_frame, text="Тема:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.new_theme = ttk.Entry(add_frame, width=30)
        self.new_theme.grid(row=3, column=1, pady=5)
        
        ttk.Button(add_frame, text="Добавить цитату", command=self.add_quote).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Фильтры
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтры", padding="10")
        filter_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=5)
        self.author_filter = ttk.Combobox(filter_frame, values=self.get_unique_authors(), width=25)
        self.author_filter.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Тема:").grid(row=0, column=2, padx=5)
        self.theme_filter = ttk.Combobox(filter_frame, values=self.get_unique_themes(), width=25)
        self.theme_filter.grid(row=0, column=3, padx=5)
        
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.refresh_history).grid(row=0, column=5, padx=10)
        
        # История
        history_frame = ttk.LabelFrame(main_frame, text="История", padding="10")
        history_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Treeview для истории
        columns = ("author", "theme", "text", "timestamp")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        self.history_tree.heading("author", text="Автор")
        self.history_tree.heading("theme", text="Тема")
        self.history_tree.heading("text", text="Цитата")
        self.history_tree.heading("timestamp", text="Дата")
        
        self.history_tree.column("author", width=150)
        self.history_tree.column("theme", width=100)
        self.history_tree.column("text", width=300)
        self.history_tree.column("timestamp", width=150)
        
        # Scrollbar для истории
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Отображение истории
        self.refresh_history()
        
        # Настройка весов сетки
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def generate_quote(self):
        # Генерация случайной цитаты из всех доступных
        all_quotes = self.default_quotes + [item for item in self.history if all(key in item for key in ["text", "author", "theme"])]
        if not all_quotes:
            messagebox.showwarning("Предупреждение", "Нет доступных цитат!")
            return
        
        random_quote = random.choice(all_quotes)
        
        # Отображение цитаты
        self.quote_text.config(state="normal")
        self.quote_text.delete(1.0, tk.END)
        self.quote_text.insert(1.0, f'"{random_quote["text"]}"')
        self.quote_text.insert(tk.END, f'\n\n— {random_quote["author"]} ({random_quote["theme"]})')
        self.quote_text.config(state="disabled")
        
        # Добавление в историю
        history_entry = {
            "text": random_quote["text"],
            "author": random_quote["author"],
            "theme": random_quote["theme"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        self.save_history()
        self.refresh_history()
        
    def add_quote(self):
        # Проверка на пустые строки
        text = self.new_quote_text.get(1.0, tk.END).strip()
        author = self.new_author.get().strip()
        theme = self.new_theme.get().strip()
        
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showerror("Ошибка", "Имя автора не может быть пустым!")
            return
        if not theme:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return
        
        # Добавление новой цитаты
        new_quote = {
            "text": text,
            "author": author,
            "theme": theme,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.history.append(new_quote)
        self.save_history()
        
        # Очистка полей ввода
        self.new_quote_text.delete(1.0, tk.END)
        self.new_author.delete(0, tk.END)
        self.new_theme.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Цитата успешно добавлена!")
        
        # Обновление фильтров
        self.author_filter["values"] = self.get_unique_authors()
        self.theme_filter["values"] = self.get_unique_themes()
        
        self.refresh_history()
        
    def apply_filter(self):
        author = self.author_filter.get()
        theme = self.theme_filter.get()
        
        filtered_history = self.history
        
        if author:
            filtered_history = [q for q in filtered_history if q["author"] == author]
        if theme:
            filtered_history = [q for q in filtered_history if q["theme"] == theme]
        
        self.display_history(filtered_history)
        
    def display_history(self, history_list):
        # Очистка дерева
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Заполнение данными
        for quote in history_list:
            self.history_tree.insert("", tk.END, values=(
                quote["author"],
                quote["theme"],
                quote["text"][:100] + "..." if len(quote["text"]) > 100 else quote["text"],
                quote.get("timestamp", "Н/Д")
            ))
    
    def refresh_history(self):
        self.display_history(self.history)
        self.author_filter.set("")
        self.theme_filter.set("")
        
    def get_unique_authors(self):
        authors = set(q["author"] for q in self.default_quotes)
        authors.update(q["author"] for q in self.history)
        return sorted(list(authors))
    
    def get_unique_themes(self):
        themes = set(q["theme"] for q in self.default_quotes)
        themes.update(q["theme"] for q in self.history)
        return sorted(list(themes))
    
    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
                self.history = []

if __name__ == "__main__":
    window = tk.Tk()
    app = QuoteGenerator(window)
    window.mainloop()
