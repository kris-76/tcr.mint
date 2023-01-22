
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from tkinter.messagebox import askokcancel
from tkinter.messagebox import WARNING
from functools import partial

class ListFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.created = False
        self.views = {}

    def grid(self, **kwargs):
        self.create_body()
        return super().grid(**kwargs)

    def pack(self, **kwargs):
        self.create_body()
        return super().grid(**kwargs)

    def place(self, **kwargs):
        self.create_body()
        return super().grid(**kwargs)

    def create_body(self):
        if self.created:
            return

        self.rowconfigure(index=0, weight=1)
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=6)

        (left_frame, self.tree) = self.create_list(self)
        left_frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NSEW)

        items = self.parent_create_views()
        for item in items:
            id = self.tree.insert('', 'end', text=item.get_name(), open=True)
            self.views[id] = item
            self.views[item.get_name()] = item

        children = self.tree.get_children()
        if len(children) > 0:
            self.tree.focus(children[0])
            self.tree.selection_set(children[0])

        self.created = True

    def create_list(self, parent):
        frame = ctk.CTkFrame(master=parent)
        frame.rowconfigure(index=0, weight=1)
        frame.columnconfigure(index=0, weight=1)

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        tree = ttk.Treeview(master=frame,
                            yscrollcommand=scrollbar.set,
                            selectmode="browse",
                            show="tree")

        scrollbar.config(command=tree.yview)
        tree.grid(row=0, column=0, padx=0, pady=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, padx=0, pady=0, sticky=tk.NS)
        tree.bind('<<TreeviewSelect>>', self.tree_selected)

        button_frame = ctk.CTkFrame(master=frame)
        delete_button = ctk.CTkButton(master=button_frame, text='-',
                                      width=28, height=28,
                                      command=self.parent_delete_item)
        add_button = ctk.CTkButton(master=button_frame, text='+',
                                   width=28, height=28,
                                   command=self.parent_add_item)
        delete_button.grid(column=0, row=0, padx=0, pady=0)
        add_button.grid(column=1, row=0, padx=0, pady=0)
        button_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=0, sticky=tk.E)

        return (frame, tree)

    def is_view_existing(self, name:str) -> bool:
        return name in self.views

    def show_item(self, name):
        for key in self.views:
            self.views[key].grid_forget()

        view = self.views[name]
        view.grid(column=1, row=0, padx=0, pady=0, sticky=tk.NSEW)

    def tree_selected(self, event):
        id = event.widget.selection()[0]
        self.show_item(id)

    def create_views(self):
        return []

    def parent_create_views(self):
        return self.create_views()

    def add_item(self):
        return None

    def parent_add_item(self):
        item = self.add_item()
        if item == None:
            return

        id = self.tree.insert('', 'end', text=item.get_name(), open=True)
        self.views[id] = item
        self.views[item.get_name()] = item

        self.tree.focus(id)
        self.tree.selection_set(id)

    def delete_item(self, name:str):
        return

    def parent_delete_item(self):
        id = self.tree.focus()

        if id == '':
            return

        answer = askokcancel(title='Confirm',
                             message=f'Delete Item: {self.views[id].get_name()}?',
                             icon=WARNING)

        if not answer:
            return

        self.tree.detach(id)
        children = self.tree.get_children()
        if len(children) > 0:
            self.tree.focus(children[0])
            self.tree.selection_set(children[0])

        name = self.views[id].get_name()
        self.views.pop(name).grid_forget()
        self.views.pop(id).grid_forget()

        self.delete_item(name)
