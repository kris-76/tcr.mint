
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
import time

from functools import partial

from tcr.project_data import ProjectData
from tcr.configuration import Configuration
from tcr.wallet import Wallet
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

    def synchronize_wallet(self):
        while True:
            try:
                for idx in range(0, 4):
                    address = self.wallet.get_delegated_payment_address(idx)
                    try:
                        utxos = self.node.get_utxos(address)
                        for utxo in utxos:
                            tx_hash = utxo.tx_hash
                            amount = utxo.amount[0].quantity
                            self.hands_treeview.insert('', 'end', iid=None, text='', values=[tx_hash, amount], open=False)
                    except blockfrost.utils.ApiError as ae:
                        if ae.status_code == 404:
                            print(f'No UTXOs: {address}')
            except Exception as e:
                print(f'Exception: {e}')
            time.sleep(60)

class WalletsFrame(ctk.CTkFrame):
    def wallet_selected_event(self, lb, arg):
        if len(lb.curselection()) == 0:
            return

        name = lb.get(lb.curselection()[0])
        print(f'selected = {name}')

    def create_wallet_list(self, parent):
        frame = ctk.CTkFrame(master=parent)

        wallets_lb = tk.Listbox(master=frame, selectmode=tk.SINGLE)
        for view in self.wallet_views:
            self.count += 1
            wallets_lb.insert(self.count, view.get_name())

        wallets_lb.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NS)
        frame.rowconfigure(index=0, weight=1)

        wallets_lb.bind('<<ListboxSelect>>', partial(self.wallet_selected_event, wallets_lb))

        button_frame = ctk.CTkFrame(master=frame)
        delete_button = ctk.CTkButton(master=button_frame, text='-', width=28, height=28, command=partial(self.delete_wallet, wallets_lb))
        add_button = ctk.CTkButton(master=button_frame, text='+', width=28, height=28, command=partial(self.add_wallet, wallets_lb))
        delete_button.grid(column=0, row=0, padx=0, pady=0)
        add_button.grid(column=1, row=0, padx=0, pady=0)
        button_frame.grid(column=0, row=1, padx=0, pady=0, sticky=tk.E)

        return frame


    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort_column(tv, _col, not reverse))


    def __init__(self, parent, settings:Configuration, user:ProjectData, node):
        ctk.CTkFrame.__init__(self, parent)

        self.settings = settings
        self.user = user
        self.node = node
        self.count = 0
        self.wallet_views = [WalletView(self, Wallet(user.get_network(), obj), self.node) for obj in self.user.get_wallets()]

        self.columnconfigure(index=0, weight=0)
        self.rowconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)

        left_frame = self.create_wallet_list(self)
        left_frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NS)

        if len(self.wallet_views) > 0:
            right_frame = self.wallet_views[0]
        else:
            right_frame = ctk.CTkFrame(master=self)
        right_frame.grid(column=1, row=0, padx=0, pady=0, sticky=tk.NSEW)

    def delete_wallet(self, lb:tk.Listbox):
        if len(lb.curselection()) == 0:
            return

        name = lb.get(lb.curselection()[0])
        lb.delete(lb.curselection()[0])
        self.user.delete_wallet(name)

    def add_wallet(self, lb:tk.Listbox):
        dialog = ctk.CTkInputDialog(text="Enter Wallet Name:", title="Create New Wallet")
        name = dialog.get_input()
        if len(name) > 0:
            for view in self.wallet_views:
                if view.get_name() == name:
                    tk.messagebox.showerror('Error', 'Duplicate Wallet Name')
                    return
            new_wallet = Wallet.create_new(name, self.user.get_network())
            self.wallet_views.append(WalletView(self, new_wallet, self.node))
            self.count += 1
            lb.insert(self.count, new_wallet.get_name())
            self.user.add_wallet(new_wallet.serialize())
