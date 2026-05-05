import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = "workouts.json"
DATE_FORMAT = "%d.%m.%Y"

# Глобальные переменные
workouts = []
filtered_workouts = []

# Виджеты
date_entry = None
type_entry = None
duration_entry = None
filter_type_entry = None
filter_date_entry = None
tree = None


def add_workout():
    """Добавление новой тренировки с проверкой ввода (без автосохранения)"""
    date_str = date_entry.get().strip()
    workout_type = type_entry.get().strip()
    duration_str = duration_entry.get().strip()

    # Проверка даты
    try:
        datetime.strptime(date_str, DATE_FORMAT)
    except ValueError:
        messagebox.showerror("Ошибка", f"Неверный формат даты. Используйте {DATE_FORMAT.replace('%d.', 'дд.').replace('%m.', 'мм.').replace('%Y', 'гггг')}")
        return

    # Проверка, что тип не пустой
    if not workout_type:
        messagebox.showerror("Ошибка", "Введите тип тренировки")
        return

    # Проверка длительности
    try:
        duration = float(duration_str)
        if duration <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
        return

    # Создаём запись
    new_record = {
        "date": date_str,
        "type": workout_type,
        "duration": duration
    }
    workouts.append(new_record)
    apply_filter()   # обновляем таблицу

    # Очищаем поля
    date_entry.delete(0, tk.END)
    type_entry.delete(0, tk.END)
    duration_entry.delete(0, tk.END)


def delete_workout():
    """Удаление выбранной тренировки (без автосохранения)"""
    selected = tree.selection()
    if not selected:
        return

    values = tree.item(selected[0])['values']
    if not values:
        return
    
    date_del, type_del, duration_del = values
    duration_del = float(duration_del)
    
    for i, w in enumerate(workouts):
        if w["date"] == date_del and w["type"] == type_del and w["duration"] == duration_del:
            del workouts[i]
            apply_filter()
            break


def apply_filter():
    """Фильтрация по введённому типу (частичное совпадение) и точной дате"""
    global filtered_workouts
    filter_type = filter_type_entry.get().strip()
    filter_date = filter_date_entry.get().strip()

    filtered = workouts.copy()

    if filter_type:
        filtered = [w for w in filtered if filter_type.lower() in w["type"].lower()]

    if filter_date:
        try:
            datetime.strptime(filter_date, DATE_FORMAT)
            filtered = [w for w in filtered if w["date"] == filter_date]
        except ValueError:
            messagebox.showerror("Ошибка", f"Неверный формат даты фильтра. Используйте {DATE_FORMAT.replace('%d.', 'дд.').replace('%m.', 'мм.').replace('%Y', 'гггг')}")
            return

    filtered_workouts = filtered
    update_table()


def reset_filter():
    """Сброс фильтров"""
    filter_type_entry.delete(0, tk.END)
    filter_date_entry.delete(0, tk.END)
    apply_filter()


def update_table():
    """Обновление таблицы Treeview"""
    for row in tree.get_children():
        tree.delete(row)

    for w in filtered_workouts:
        tree.insert("", tk.END, values=(w["date"], w["type"], w["duration"]))


def save_data(filename=None):
    """Сохраняет данные в JSON-файл (ручное сохранение)"""
    if filename is None:
        filename = DATA_FILE
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(workouts, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")


def load_data(filename=None):
    """Загружает данные из JSON-файла (ручная загрузка)"""
    global workouts
    if filename is None:
        filename = DATA_FILE
    if not os.path.exists(filename):
        messagebox.showwarning("Предупреждение", f"Файл {filename} не найден. Начинаем с пустого списка.")
        workouts = []
    else:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                workouts = json.load(f)
            messagebox.showinfo("Успех", f"Загружено {len(workouts)} записей из {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            workouts = []
    apply_filter()


def save_as():
    """Сохранить данные в выбранный пользователем JSON-файл"""
    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filename:
        save_data(filename)


def load_from():
    """Загрузить данные из выбранного пользователем JSON-файла"""
    filename = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filename:
        load_data(filename)


def build_ui(root):
    """Создаёт все элементы интерфейса"""
    global date_entry, type_entry, duration_entry, filter_type_entry, filter_date_entry, tree

    # --- Верхняя панель: ввод новой тренировки ---
    input_frame = ttk.LabelFrame(root, text="Новая тренировка", padding=10)
    input_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    date_entry = ttk.Entry(input_frame, width=15)
    date_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    type_entry = ttk.Entry(input_frame, width=20)
    type_entry.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    duration_entry = ttk.Entry(input_frame, width=10)
    duration_entry.grid(row=0, column=5, padx=5, pady=5)

    add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=add_workout)
    add_btn.grid(row=0, column=6, padx=10, pady=5)

    # --- Панель фильтрации ---
    filter_frame = ttk.LabelFrame(root, text="Фильтр", padding=10)
    filter_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    filter_type_entry = ttk.Entry(filter_frame, width=20)
    filter_type_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(filter_frame, text="(оставьте пустым для всех)", font=("Arial", 8)).grid(row=0, column=2, padx=5, pady=5)

    ttk.Label(filter_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=3, padx=5, pady=5, sticky="e")
    filter_date_entry = ttk.Entry(filter_frame, width=15)
    filter_date_entry.grid(row=0, column=4, padx=5, pady=5)

    filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=apply_filter)
    filter_btn.grid(row=0, column=5, padx=5, pady=5)

    reset_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=reset_filter)
    reset_btn.grid(row=0, column=6, padx=5, pady=5)

    # --- Блок кнопок управления записями ---
    action_frame = ttk.Frame(root)
    action_frame.pack(fill="x", padx=10, pady=5)

    delete_btn = ttk.Button(action_frame, text="Удалить выбранную тренировку", command=delete_workout)
    delete_btn.pack(side="left", padx=5)

    # --- Кнопки сохранения/загрузки ---
    file_frame = ttk.Frame(root)
    file_frame.pack(fill="x", padx=10, pady=5)

    save_btn = ttk.Button(file_frame, text="Сохранить в JSON (по умолчанию)", command=lambda: save_data())
    save_btn.pack(side="left", padx=5)

    save_as_btn = ttk.Button(file_frame, text="Сохранить как...", command=save_as)
    save_as_btn.pack(side="left", padx=5)

    load_btn = ttk.Button(file_frame, text="Загрузить из JSON (по умолчанию)", command=lambda: load_data())
    load_btn.pack(side="left", padx=5)

    load_from_btn = ttk.Button(file_frame, text="Загрузить из...", command=load_from)
    load_from_btn.pack(side="left", padx=5)

    # --- Таблица тренировок ---
    table_frame = ttk.Frame(root)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("date", "type", "duration")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    tree.heading("date", text="Дата")
    tree.heading("type", text="Тип тренировки")
    tree.heading("duration", text="Длительность (мин)")
    tree.column("date", width=120)
    tree.column("type", width=200)
    tree.column("duration", width=120)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def main():
    root = tk.Tk()
    root.title("Трекер тренировок")
    root.geometry("800x600")

    build_ui(root)
    # Не загружаем данные автоматически
    root.mainloop()


if __name__ == "__main__":
    main()