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

from tcr.ui.ok_cancel_dialog import OkCancelDialog

class RoyaltyTokenDialog(OkCancelDialog):
    def __init__(self, parent):
        OkCancelDialog.__init__(self, parent, 'Create Royalty Token')

    def body(self, master):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)

        self.address = tk.StringVar()
        self.rate = tk.StringVar()

        label = ctk.CTkLabel(master=master, text='Address:')
        label.grid(column=0, row=0, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=master, width=250,
                             textvariable=self.address,
                             placeholder_text='Address')
        value.grid(column=1, row=0, sticky=tk.EW, padx=0, pady=5)

        label = ctk.CTkLabel(master=master, text='Rate:')
        label.grid(column=0, row=1, sticky=tk.E, padx=5, pady=5)

        value = ctk.CTkEntry(master=master, width=250,
                             textvariable=self.rate)
        value.grid(column=1, row=1, sticky=tk.EW, padx=0, pady=5)

    def apply(self):
        return {'address': self.address.get(), 'rate': self.rate.get()}
