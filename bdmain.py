import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
import psycopg2
import pandas as pd
import os
import prettytable

class MainInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("kursovaya")

        # Подключение к PostgreSQL
        self.connection = psycopg2.connect(
            database="kursach3",
            user="postgres",
            password="20133102es",
            host="localhost",
            port="5432"
        )
        self.cursor = self.connection.cursor()

        self.button_complex_query = tk.Button(root, text="Отчет", command=self.show_complex_query_window)
        self.button_save_to_excel = tk.Button(root, text="Сохранить в Excel", command=self.save_to_excel)
        # Создание и заполнение выпадающего списка таблиц
        self.tables_label = tk.Label(root, text="Выберите таблицу:")
        self.tables_combobox = ttk.Combobox(root, values=self.get_table_names())
        self.tables_combobox.bind("<<ComboboxSelected>>", self.load_table_data)

        # Создание Treeview для отображения данных таблицы
        self.tree = ttk.Treeview(root)
        self.tree.grid(row=1, column=0, columnspan=4, pady=10)

        # Кнопка для обновления данных
        self.button_refresh = tk.Button(root, text="Обновить", command=self.load_table_data)
        self.button_refresh.grid(row=2, column=0, padx=5)

        # Кнопки для управления данными
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=2, column=1, columnspan=3, pady=10)

        self.button_view = tk.Button(self.button_frame, text="Просмотр", command=self.view_data)
        self.button_add = tk.Button(self.button_frame, text="Добавить", command=self.add_data)
        self.button_update = tk.Button(self.button_frame, text="Изменить", command=self.update_data)
        self.button_delete = tk.Button(self.button_frame, text="Удалить", command=self.delete_data)

        # Расположение элементов на форме
        self.tables_label.grid(row=0, column=0, padx=10, pady=10)
        self.tables_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.button_view.grid(row=0, column=2, padx=5)
        self.button_add.grid(row=0, column=3, padx=5)
        self.button_update.grid(row=0, column=4, padx=5)
        self.button_delete.grid(row=0, column=5, padx=5)
        self.button_complex_query.grid(row=2, column=7, padx=5)
        self.button_save_to_excel.grid(row=2, column=8, padx=5)

    def get_table_names(self):
        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        return [table[0] for table in self.cursor.fetchall()]

    def load_table_data(self, event=None):
        table_name = self.tables_combobox.get()
        if table_name:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            data = self.cursor.fetchall()

            # Очистка предыдущих записей в Treeview
            self.tree.delete(*self.tree.get_children())

            if data:
                # Загрузка данных в Treeview только если есть данные
                columns = [column[0] for column in self.cursor.description]
                self.tree["columns"] = columns
                for col in columns:
                    self.tree.heading(col, text=col.capitalize())
                    self.tree.column(col, anchor=tk.CENTER, width=100)

                for row in data:
                    self.tree.insert("", tk.END, values=row)

    def get_data_from_tree(self):
        # Получение выделенной строки из Treeview
        selected_item = self.tree.selection()
        if selected_item:
            return self.tree.item(selected_item, "values")
        return None

    def view_data(self):
        self.load_table_data()

    def add_data(self):
        table_name = self.tables_combobox.get()
        if table_name:
            columns = [column[0] for column in self.cursor.description]
            new_data = simpledialog.askstring("Добавление данных", f"Введите данные через запятую ({', '.join(columns)}):")
            if new_data:
                try:
                    self.cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['%s']*len(new_data.split(',')))})", tuple(new_data.split(',')))
                    self.connection.commit()
                    self.load_table_data()  # Обновляем данные после добавления
                    messagebox.showinfo("Успех", "Новая запись успешно добавлена")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def update_data(self):
        table_name = self.tables_combobox.get()
        if table_name:
            data = self.get_data_from_tree()
            if data:
                # Получаем список столбцов
                columns = [column[0] for column in self.cursor.description]

                # Пример использования simpledialog для получения новых значений
                new_values = []
                for column in columns:
                    new_value = simpledialog.askstring("Изменение данных", f"Введите новое значение для {column}:")
                    if new_value is not None:
                        new_values.append(new_value)

                # Ваш код для обновления данных в базе данных
                if new_values:
                    update_query = f"UPDATE {table_name} SET {', '.join([f'{column}=%s' for column in columns])} WHERE {columns[0]}=%s"
                    self.cursor.execute(update_query, tuple(new_values + [data[0]]))
                    self.connection.commit()
                    self.load_table_data()  # Обновляем данные после изменения
                    messagebox.showinfo("Успех", "Запись успешно изменена")
            else:
                messagebox.showinfo("Изменение данных", "Выберите запись для изменения")

    def delete_data(self):
        table_name = self.tables_combobox.get()
        if table_name:
            data = self.get_data_from_tree()
            if data:
                column_name = simpledialog.askstring("Удаление данных",
                                                     "Введите название столбца, по которому удалять:")
                if column_name:
                    try:
                        self.cursor.execute(f"DELETE FROM {table_name} WHERE {column_name}=%s", (data[0],))
                        self.connection.commit()
                        self.load_table_data()  # Обновляем данные после удаления
                        messagebox.showinfo("Успех", "Запись успешно удалена")
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
            else:
                messagebox.showinfo("Удаление данных", "Выберите запись для удаления")

    def show_complex_query_window(self):
        # Создание нового окна для ввода сложного запроса
        complex_query_window = tk.Toplevel(self.root)
        complex_query_window.title("Отчет")

        # Многострочное текстовое поле для ввода SQL-запроса
        query_text = scrolledtext.ScrolledText(complex_query_window, wrap=tk.WORD, width=40, height=10)
        query_text.grid(row=0, column=0, padx=10, pady=10)

        # Выпадающий список с выбором запроса
        query_options = [
            "Запрос 1",
            "Запрос 2",
            "Запрос 3",
            "Запрос 4",
            "Запрос 5",
            "Запрос 6"
        ]
        query_combobox = ttk.Combobox(complex_query_window, values=query_options)
        query_combobox.set("Выберите запрос")
        query_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Кнопка для выполнения сложного запроса
        execute_button = tk.Button(complex_query_window, text="Выполнить отчет",
                                   command=lambda: self.execute_complex_query(query_combobox.get(), query_text.get("1.0", tk.END)))
        execute_button.grid(row=1, column=0, columnspan=2, pady=10)

    def execute_complex_query(self, selected_query, query):
        try:
            # Выполнение выбранного запроса
            if selected_query == "Запрос 1":
                result = self.query1()
            elif selected_query == "Запрос 2":
                result = self.query2()
            elif selected_query == "Запрос 3":
                result = self.query3()
            elif selected_query == "Запрос 4":
                result = self.query4()
            elif selected_query == "Запрос 5":
                result = self.query5()
            elif selected_query == "Запрос 6":
                result = self.query6()
            else:
                result = None

            # Отображение результата запроса
            if result:
                self.display_result(result)
        except Exception as e:
            messagebox.showerror("Ошибка выполнения запроса", f"Произошла ошибка: {e}")

    def display_result(self, result):
        # Используем prettytable для форматирования данных
        table = prettytable.PrettyTable()
        table.field_names = [desc[0] for desc in self.cursor.description]
        table.add_rows(result)

        # Создаем новое окно для отображения результата
        result_window = tk.Toplevel(self.root)
        result_window.title("Результат запроса")

        # Создаем текстовое поле для вывода отформатированных данных
        result_text = tk.Text(result_window, wrap=tk.WORD, width=80, height=20)
        result_text.insert(tk.END, str(table))
        result_text.config(state=tk.DISABLED)
        result_text.pack(padx=10, pady=10)

        # Прокрутка текстового поля
        scroll = tk.Scrollbar(result_window, command=result_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.config(yscrollcommand=scroll.set)

    def save_to_excel(self):
        # Открываем окно с запросами для выбора запроса
        complex_query_window = tk.Toplevel(self.root)
        complex_query_window.title("Сохранение в Excel")

        # Многострочное текстовое поле для ввода SQL-запроса
        query_text = scrolledtext.ScrolledText(complex_query_window, wrap=tk.WORD, width=40, height=10)
        query_text.grid(row=0, column=0, padx=10, pady=10)

        # Выпадающий список с выбором запроса
        query_options = [
            "Запрос 1",
            "Запрос 2",
            "Запрос 3",
            "Запрос 4",
            "Запрос 5",
            "Запрос 6"
        ]
        query_combobox = ttk.Combobox(complex_query_window, values=query_options)
        query_combobox.set("Выберите запрос")
        query_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Кнопка для выполнения запроса и сохранения в Excel
        execute_button = tk.Button(complex_query_window, text="Сохранить в Excel",
                                   command=lambda: self.save_query_to_excel(query_combobox.get(),
                                                                            query_text.get("1.0", tk.END)))
        execute_button.grid(row=1, column=0, columnspan=2, pady=10)

    def save_query_to_excel(self, selected_query, query):
        try:
            # Выполнение выбранного запроса
            result = None
            if selected_query == "Запрос 1":
                result = self.query1()
            elif selected_query == "Запрос 2":
                result = self.query2()
            elif selected_query == "Запрос 3":
                result = self.query3()
            elif selected_query == "Запрос 4":
                result = self.query4()
            elif selected_query == "Запрос 5":
                result = self.query5()
            elif selected_query == "Запрос 6":
                result = self.query6()

            # Если результат получен, сохраняем его в Excel
            if result:
                # Создаем DataFrame из результата запроса
                df = pd.DataFrame(result)

                # Открываем окно сохранения файла
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                            filetypes=[("Файлы Excel", "*.xlsx")])
                if file_path:
                    # Сохраняем DataFrame в Excel
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Сохранение в Excel", "Результат успешно сохранен в Excel")

                    # Предлагаем открыть файл
                    open_file = messagebox.askyesno("Открыть файл", "Хотите открыть сохраненный файл?")
                    if open_file:
                        self.open_excel_file(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения в Excel", f"Произошла ошибка: {e}")

    def open_excel_file(self, file_path):
        try:
            # Проверяем, существует ли файл
            if os.path.exists(file_path):
                # Открываем файл с использованием системного приложения по умолчанию
                os.system(f'start excel "{file_path}"')
            else:
                messagebox.showwarning("Файл не найден", "Файл не существует.")
        except Exception as e:
            messagebox.showerror("Ошибка открытия файла", f"Произошла ошибка: {e}")

    def query1(self):
        self.cursor.execute('''
        SELECT r.title, pl.price, pl.expenses, (pl.price + pl.expenses) AS total_cost
        FROM price_list pl
        JOIN rate r ON pl.id_rate = r.id_rate
        ''')
        return self.cursor.fetchall()

    def query2(self):
        self.cursor.execute('''
        SELECT c.full_name, SUM(pl.price + pl.expenses) AS total_cost
        FROM client c
        JOIN subscribe s ON c.id_client = s.id_client
        JOIN rate r ON s.id_rate = r.id_rate
        JOIN price_list pl ON r.id_rate = pl.id_rate
        GROUP BY c.id_client
        HAVING SUM(pl.price + pl.expenses) > (SELECT AVG(price + expenses) FROM price_list);
        ''')
        return self.cursor.fetchall()

    def query3(self):
        self.cursor.execute('''
        SELECT r.title, pl.price
        FROM price_list pl
        JOIN rate r ON pl.id_rate = r.id_rate
        WHERE pl.price = (SELECT MAX(price) FROM price_list);
        ''')
        return self.cursor.fetchall()

    def query4(self):
        self.cursor.execute('''
        SELECT c.*
        FROM client c
        JOIN subscribe s ON c.id_client = s.id_client
        JOIN rate r ON s.id_rate = r.id_rate
        JOIN price_list p ON r.id_rate = p.id_rate
        WHERE p.expenses > (SELECT AVG(expenses) FROM price_list);
        ''')
        return self.cursor.fetchall()

    def query5(self):
        self.cursor.execute('''
        SELECT e.type_equipment, COUNT(c.id_client) AS client_count
        FROM equipment e
        LEFT JOIN rate r ON e.id_equipment = r.id_equipment
        LEFT JOIN subscribe s ON r.id_rate = s.id_rate
        LEFT JOIN client c ON s.id_client = c.id_client
        GROUP BY e.type_equipment;
        ''')
        return self.cursor.fetchall()

    def query6(self):
        self.cursor.execute('''
        SELECT e.type_equipment, SUM(e.price) AS total_price
        FROM equipment e
        GROUP BY e.type_equipment;
        ''')
        return self.cursor.fetchall()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainInterface(root)
    root.mainloop()