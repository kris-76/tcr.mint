
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
import time

from functools import partial

from tcr.project_data import ProjectData
from tcr.configuration import Configuration
from tcr.wallet import Wallet
from tcr.ui.list_frame import ListFrame
import blockfrost

class WalletView(ctk.CTkFrame):
    def __init__(self, parent, wallet:Wallet, node):
        ctk.CTkFrame.__init__(self, parent)

        self.wallet = wallet
        self.node = node
        columns = ("UTXO", "Lovelace")
        self.hands_scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.hands_treeview = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")

        self.hands_treeview.column("UTXO", width=400, minwidth=200)
        self.hands_treeview.column("Lovelace", width=20, minwidth=10)

        self.hands_treeview.heading("UTXO", text="UTXO", anchor=tk.CENTER, command=lambda _col="UTXO": self.treeview_sort_column(self.hands_treeview, _col, False))
        self.hands_treeview.heading("Lovelace", text="Lovelace", anchor=tk.CENTER, command=lambda _col="Lovelace": self.treeview_sort_column(self.hands_treeview, _col, False))

        self.hands_treeview.configure(yscrollcommand=self.hands_scrollbar.set)
        self.hands_scrollbar.configure(command=self.hands_treeview.yview)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)
        self.hands_treeview.grid(row=0, column=0, sticky=tk.NSEW)
        self.hands_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.synchronize_thread = threading.Thread(target=self.synchronize_wallet,
                                                   daemon=True)
        self.synchronize_thread.start()

    def get_name(self):
        return self.wallet.get_name()

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort_column(tv, _col, not reverse))

    def synchronize_wallet(self):
        while True:
            current_utxos = []
            try:
                for idx in range(0, 4):
                    address = self.wallet.get_delegated_payment_address(idx)
                    try:
                        utxos = self.node.get_utxos(address)
                        current_utxos.extend(utxos)
                    except blockfrost.utils.ApiError as ae:
                        pass

                    address = self.wallet.get_payment_address(idx)
                    try:
                        utxos = self.node.get_utxos(address)
                        current_utxos.extend(utxos)
                    except blockfrost.utils.ApiError as ae:
                        pass
            except Exception as e:
                print(f'Exception: {e}')

            # if a current utxo isn't in the view, add it
            for utxo in current_utxos:
                found = False
                children = self.hands_treeview.get_children()
                for child in children:
                    values = self.hands_treeview.item(child)['values']
                    if utxo.tx_hash == values[0]:
                        found = True
                        break

                if not found:
                    tx_hash = utxo.tx_hash
                    amount = utxo.amount[0].quantity
                    self.hands_treeview.insert('', 'end', iid=None, text='', values=[tx_hash, amount], open=False)

            # if a utxo is in the view but not current, remove it
            children = self.hands_treeview.get_children()
            for child in children:
                values = self.hands_treeview.item(child)['values']
                found = False
                for utxo in current_utxos:
                    if utxo.tx_hash == values[0]:
                        found = True
                        break
                if not found:
                    self.hands_treeview.detach(child)

            time.sleep(30)

class WalletsFrame(ListFrame):
    def __init__(self, parent, settings:Configuration, user:ProjectData, node):
        super().__init__(parent)

        self.settings = settings
        self.user = user
        self.node = node

    def create_views(self):
        return [WalletView(self, Wallet(self.user.get_network(), obj), self.node)
                for obj in self.user.get_wallets()]

    def add_item(self):
        dialog = ctk.CTkInputDialog(text="Enter Wallet Name:",
                                    title="Create New Wallet")
        name = dialog.get_input()
        if name == None or len(name) == 0:
            return

        if self.is_view_existing(name) != False:
            tk.messagebox.showerror('Error', 'Duplicate Wallet Name')
            return

        new_wallet = Wallet.create_new(name, self.user.get_network())
        view = WalletView(self, new_wallet, self.node)
        return view

    def delete_item(self, name):
        self.user.delete_wallet(name)
