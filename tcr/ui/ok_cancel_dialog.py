
import tkinter as tk
import customtkinter as ctk
from tkcalendar import Calendar
from functools import partial

class OkCancelDialog(ctk.CTkToplevel):
    def __init__(self, parent, title:str):
        ctk.CTkToplevel.__init__(self, parent)

        self.ok = False
        self.parent = parent
        self.result = None

        self.title(title)
        self.resizable(height=True, width=True)
        self.grab_set() # makes it modal

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.frame = ctk.CTkFrame(self)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NSEW)

        self.body(master=self.frame)

        bf = ctk.CTkFrame(master=self)

        def close_dialog(ok:bool):
            self.ok = ok
            self.result = None

            if not self.ok:
                self.destroy()
                return

            self.result = self.apply()
            if self.result:
                self.destroy()

        button = ctk.CTkButton(bf, text="OK", width=75, command=partial(close_dialog, ok=True))
        button.grid(column=0, row=0, padx=5, pady=0, sticky=tk.E)

        button = ctk.CTkButton(bf, text="Cancel", width=75, command=partial(close_dialog, ok=False))
        button.grid(column=1, row=0, padx=5, pady=0, sticky=tk.W)

        bf.grid(column=0, row=1, padx=5, pady=5)

        self.update()

    def is_ok(self):
        return self.ok

    def get_result(self):
        return self.result

    def body(self, master):
        return

    def apply(self):
        return None
