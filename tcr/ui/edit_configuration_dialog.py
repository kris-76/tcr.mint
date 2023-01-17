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
import tkinter.ttk as ttk
import customtkinter as ctk

from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

class EditConfigurationDialog(ctk.CTkToplevel):
    def configure_root(self):
        self.title('NFT Mint: Settings')
        self.resizable(height=False, width=True)
        self.grab_set()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=0)

    def create_data_file_setting(self, row:int):
        label = ctk.CTkLabel(master=self, text="data file:")
        label.grid(column=0, row=row, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=self, width=450, placeholder_text='path to data file')
        value.delete(0, tk.END)
        value.insert(0, self.settings.get_data_file())
        value.grid(column=1, row=row, sticky=tk.EW, padx=0, pady=5)

        def browse():
            filename = asksaveasfilename(master=self, defaultextension='data', filetypes=[('data', '*.data')])
            value.delete(0, tk.END)
            value.insert(0, filename)
            self.settings.set_data_file(filename)

        button = ctk.CTkButton(master=self, text='...', width=28, command=browse)
        button.grid(column=2, row=row, padx=5, pady=5)

    def create_blockfrost_node_setting(self, row:int):
        label = ctk.CTkLabel(self, text ="BlockFrost Node Project ID:")
        label.grid(sticky=tk.E, row=row, column=0, padx=5, pady=5)

        text_value = tk.StringVar()
        value = ctk.CTkEntry(self, width=450, textvariable=text_value)
        value.delete(0, tk.END)
        value.insert(0, self.settings.get_blockfrost_node_project_id())
        value.grid(column=1, row=row, sticky=tk.EW, padx=0, pady=5)

        def update_settings(*args):
            self.settings.set_blockfrost_node_project_id(text_value.get())

        text_value.trace('w', update_settings)

    def create_network_option(self, row:int):
        label = ctk.CTkLabel(self, text ="Network:")
        label.grid(column=0, row=row, padx=5, pady=5, sticky=tk.E)

        value = ctk.CTkComboBox(self,
                                values=['mainnet', 'preprod', 'preview', 'testnet'],
                                variable=self.network_value)
        value.grid(column=1, row=row, sticky=tk.EW, padx=0, pady=5)

    def create_ok_button(self, row:int):
        button = ctk.CTkButton(self, text="OK", command=self.destroy)
        button.grid(column=1, row=row, sticky=tk.E, padx=5, pady=5)

    def get_network(self) -> str:
        return self.network_value.get()

    def __init__(self, parent, settings):
        ctk.CTkToplevel.__init__(self, parent)
        self.settings = settings
        self.network_value = tk.StringVar(value='')

        self.configure_root()
        self.create_data_file_setting(row=0)
        self.create_blockfrost_node_setting(row=1)
        self.create_network_option(row=2)
        self.create_ok_button(row=3)

        self.update()
