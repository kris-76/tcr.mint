#
# Copyright 2021-2023 The Card Room
#
# MIT License:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
import customtkinter as ctk
import datetime

from tcr.ui.date_picker_dialog import DatePickerDialog
from tcr.ui.ok_cancel_dialog import OkCancelDialog
from tcr.project_data import ProjectData

class CreatePolicyDialog(OkCancelDialog):
    def __init__(self, parent, user:ProjectData):
        self.user = user
        OkCancelDialog.__init__(self, parent, 'Policies: Create New Policy ID')

    def body(self, master):
        self.name_var = tk.StringVar()
        self.lock_date_var = tk.StringVar()
        self.lock_date = None

        label = ctk.CTkLabel(master=master, text='Wallet:')
        label.grid(column=0, row=0, sticky=tk.E, padx=5, pady=5)

        self.wallet_var = ctk.StringVar(value='')
        wallet_values = []

        for wallet in self.user.get_wallets():
            wallet_values.append(wallet['name'])

        value = ctk.CTkComboBox(master=master,
                                values=wallet_values,
                                variable=self.wallet_var)
        value.grid(column=1, row=0, sticky=tk.EW, padx=0, pady=5)


        label = ctk.CTkLabel(master=master, text='Name:')
        label.grid(column=0, row=1, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=master, width=250,
                             textvariable=self.name_var,
                             placeholder_text='User friendly name')
        value.grid(column=1, row=1, sticky=tk.EW, padx=0, pady=5)


        label = ctk.CTkLabel(master=master, text="Lock Date:")
        label.grid(column=0, row=2, sticky=tk.E, padx=5, pady=5)

        def handle_click(arg):
            dialog = DatePickerDialog(self)
            self.wait_window(dialog)
            if dialog.is_ok():
                self.lock_date = dialog.get_result()['date']
                self.lock_date_var.set(dialog.get_result()['date'])

        value = ctk.CTkEntry(master=master, width=250,
                             textvariable=self.lock_date_var,
                             placeholder_text='Policy Locking Date')
        value.bind("<1>", handle_click)
        value.grid(column=1, row=2, sticky=tk.EW, padx=0, pady=5)

    def apply(self):
        if len(self.wallet_var.get()) == 0:
            tk.messagebox.showerror('Error', 'Select a wallet for signing transactions')
            return None

        if len(self.name_var.get()) == 0:
            tk.messagebox.showerror('Error', 'Enter a policy name')
            return None

        if self.lock_date == None:
            tk.messagebox.showerror('Error', 'Enter a lock date')
            return None

        now = datetime.date.today()
        difference = self.lock_date - now
        if difference.total_seconds() <= 0:
            tk.messagebox.showerror('Error', 'Date must be at least 1 day in the future')

        return {'name': self.name_var.get(),
                'wallet': self.wallet_var.get(),
                'lock_date': self.lock_date,
                'seconds': int(difference.total_seconds())}
