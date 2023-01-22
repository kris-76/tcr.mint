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

from tcr.ui.ok_cancel_dialog import OkCancelDialog
from tcr.project_data import ProjectData
from tkinter.filedialog import asksaveasfilename

class CreateProjectDialog(OkCancelDialog):
    def __init__(self, parent, user:ProjectData):
        self.user = user
        OkCancelDialog.__init__(self, parent, 'Projects: Create New Project')

    def body(self, master):
        self.name_var = tk.StringVar(value='')
        self.policy_var = ctk.StringVar(value='')
        self.nft_data_var = ctk.StringVar(value='')

        label = ctk.CTkLabel(master=master, text='Name:')
        label.grid(column=0, row=0, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=master, width=250,
                             textvariable=self.name_var,
                             placeholder_text='User friendly name')
        value.grid(column=1, row=0, sticky=tk.EW, padx=0, pady=5)


        label = ctk.CTkLabel(master=master, text='Policy:')
        label.grid(column=0, row=1, sticky=tk.E, padx=5, pady=5)

        policy_values = []
        for policy in self.user.get_policies():
            policy_values.append(policy['name'])

        value = ctk.CTkComboBox(master=master,
                                values=policy_values,
                                variable=self.policy_var)
        value.grid(column=1, row=1, sticky=tk.EW, padx=0, pady=5)


        label = ctk.CTkLabel(master=master, text="NFT Data File:")
        label.grid(column=0, row=2, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=master, width=450, textvariable=self.nft_data_var, placeholder_text='path to data file')
        value.grid(column=1, row=2, sticky=tk.EW, padx=0, pady=5)

        def browse():
            filename = asksaveasfilename(master=master, defaultextension='json', filetypes=[('json', '*.json')])
            self.nft_data_var.set(filename)

        button = ctk.CTkButton(master=master, text='...', width=28, command=browse)
        button.grid(column=2, row=2, padx=5, pady=5)



    def apply(self):
        if len(self.name_var.get()) == 0:
            tk.messagebox.showerror('Error', 'Enter a project name')
            return None

        if len(self.policy_var.get()) == 0:
            tk.messagebox.showerror('Error', 'Select a policy for the project')
            return None

        if len(self.nft_data_var.get()) == 0:
            tk.messagebox.showerror('Error', 'Enter a data file')
            return None

        return {
            'name': self.name_var.get(),
            'policy': self.policy_var.get(),
            'nft_data': self.nft_data_var.get()
        }
