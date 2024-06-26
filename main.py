import tkinter as tk
from tkinter import messagebox
import psycopg2
from bdmain import MainInterface

# Создание подключения к PostgreSQL
connection = psycopg2.connect(
    database="",
    user="",
    password="",
    host="",
    port=""
)
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(50))")
connection.commit()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Вход и регистрация")

        self.label_username = tk.Label(root, text="Имя пользователя:")
        self.entry_username = tk.Entry(root)

        self.label_password = tk.Label(root, text="Пароль:")
        self.entry_password = tk.Entry(root, show="*")

        self.button_register = tk.Button(root, text="Зарегистрироваться", command=self.register)
        self.button_login = tk.Button(root, text="Войти", command=self.login)

        self.label_username.grid(row=0, column=0, padx=10, pady=10)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10)

        self.label_password.grid(row=1, column=0, padx=10, pady=10)
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        self.button_register.grid(row=2, column=0, columnspan=2, pady=10)
        self.button_login.grid(row=3, column=0, columnspan=2, pady=10)
        self.main_interface_opened = False
    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Пользователь уже существует")
            else:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                connection.commit()
                messagebox.showinfo("Успех", "Регистрация прошла успешно")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            if cursor.fetchone():
                messagebox.showinfo("Успех", "Вход выполнен успешно")
            else:
                messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

        self.show_main_interface()
        if not self.main_interface_opened:
            self.show_main_interface()
    def show_main_interface(self):
        self.root.withdraw()
        self.root.destroy()
        self.main_interface_opened = True
        root_main = tk.Tk()
        app_main = MainInterface(root_main)
        root_main.mainloop()

    def on_main_interface_close(self):
        self.main_interface_opened = False
        self.root.deiconify()

root = tk.Tk()
app = LoginApp(root)
root.mainloop()

connection.close()

