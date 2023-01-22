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

class CreateNftDefinitionDialog(OkCancelDialog):
    def __init__(self, parent):
        OkCancelDialog.__init__(self, parent, 'NFTs: Define')

    def body(self, master):
        self.name_var = tk.StringVar()
        self.type_var = tk.IntVar()

        label = ctk.CTkLabel(master=master, text='Name:')
        label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=master, width=250,
                             textvariable=self.name_var,
                             placeholder_text='User friendly name')
        value.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=0, pady=5)


        label = ctk.CTkLabel(master=master, text='Type:')
        label.grid(row=1, column=0, columnspan=1, sticky=tk.E, padx=5, pady=5)

        rb1 = ctk.CTkRadioButton(master=master, text="Card", variable=self.type_var, value=1)
        rb2 = ctk.CTkRadioButton(master=master, text="Layers", variable=self.type_var, value=2)

        rb1.grid(row=1, column=1, padx=0, pady=0)
        rb2.grid(row=1, column=2, padx=0, pady=0)

    def apply(self):
        if len(self.name_var.get()) == 0:
            tk.messagebox.showerror('Error', 'Enter a name')
            return None

        return {
            'name': self.name_var.get(),
            'type': self.type_var.get()
        }
