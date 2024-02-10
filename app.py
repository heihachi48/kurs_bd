import tkinter as tk
from main import LoginApp

if __name__ == "__main__":
    root_login = tk.Tk()
    app_login = LoginApp(root_login)
    root_login.mainloop()