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
from tkcalendar import Calendar

from tcr.ui.ok_cancel_dialog import OkCancelDialog

class DatePickerDialog(OkCancelDialog):
    def __init__(self, parent):
        OkCancelDialog.__init__(self, parent, 'Select Date')

    def body(self, master):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.calendar = Calendar(master, font='lucida 26', selectmode = 'day')
        self.calendar.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NSEW)

    def apply(self):
        return {'date': self.calendar.selection_get()}
