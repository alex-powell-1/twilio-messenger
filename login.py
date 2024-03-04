from os import environ
import tkinter
# Set to disable console output upon initialization
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import ttkbootstrap as ttk
from tkinter import messagebox, PhotoImage, scrolledtext
from sys import platform
import json
import sys
import creds
import theme
class LoginWindow:
    def __init__(self):
        self.parent = ttk.Window()
        style = ttk.Style()
        style.configure('my.TButton', font=(theme.main_font, 11), background=theme.login_button_color, padding=10)
        self.style = ttk.Style()
        self.style.configure('my.TButton', font=(theme.main_font, 11), background=theme.login_button_color, padding=10)
        self.frame = ttk.Frame(self.parent)
        self.parent.tk.call('wm', 'iconphoto', self.parent._w, PhotoImage(file=creds.application_icon))
        self.parent.title(theme.login_title)
        self.screen_width = self.parent.winfo_screenwidth()
        self.screen_height = self.parent.winfo_screenheight()
        self.parent.geometry(f"{round(self.screen_width * .25)}x{round(self.screen_height * .8)}")
        self.parent.position_center()
        self.parent.tk.call('wm', 'iconphoto', self.parent._w, PhotoImage(file=creds.application_icon))
        self.logo = ttk.PhotoImage(file=creds.application_logo)
        self.logo_label = ttk.Label(self.frame, image=self.logo)
        self.logo_label.pack(side="top")
        # Create and place the username label and entry
        self.username_label = ttk.Label(self.frame, text="Username:", justify="center", font=theme.login_label_font)
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.frame, justify="center", font=theme.login_label_font)
        self.username_entry.pack(pady=5)
        self.username_entry.focus_set()
        # Create and place the password label and entry
        self.password_label = ttk.Label(self.frame, text="Password:", justify="center", font=theme.login_label_font)
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.frame, show="*", justify="center", font=theme.login_label_font)
        self.password_entry.pack(pady=5)
        self.password_entry.bind('<Return>', self.submit_form)
        # Create and place the login button
        self.login_button = ttk.Button(self.frame, text="Login", command=self.validate_login, style='my.TButton')
        self.login_button.pack(pady=15)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.frame.pack(expand=True)
        # Start the Tkinter event loop
        self.parent.mainloop()

    def validate_login(self):
        global userid
        global user
        userid = self.username_entry.get()
        password = self.password_entry.get()

        try:
            if platform == "win32":
                file = open(creds.windows_user_path)
            else:
                file = open(creds.mac_user_path)
        except FileNotFoundError:
            if platform == "win32":
                messagebox.showerror("Login Failed", "Network error:\n\nCannot find user file.")
            else:
                messagebox.showerror("Login Failed", "Network error:\n\nCannot find user file.\n\n"
                                                     "Connect to share and try again.")
        else:
            data = json.load(file)

        for k, v in data.items():
            if k == userid and v['key'] == password:
                messagebox.showinfo("Login Successful", f"Welcome, {v['name']}!")
                # Destroy first window
                self.parent.destroy()
                # reset style
                ttk.Style.instance = None
                user = v['full_name']
                return
        else:
            messagebox.showerror("Login Failed", "Contact Administrator.")
            self.parent.focus()
            self.password_entry.focus_set()
            return

    def submit_form(self, event):
        self.validate_login()
        return

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.parent.destroy()
            sys.exit()
        else:
            self.password_entry.focus_set()
