import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk

from functools import partial

from tcr.configuration import Configuration
from tcr.ui.edit_configuration_dialog import EditConfigurationDialog
from tcr.ui.wallets_frame import WalletsFrame
from tcr.ui.policies_frame import PoliciesFrame

class GuiMain(ctk.CTk):
    def create_menu(self):
        self.option_add('*tearOff', tk.FALSE)

        menu = tk.Menu(self, tearoff=0)
        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label='Exit', font=self.default_font,
                            command=self.quit)
        menu.add_cascade(label='File', font=self.default_font, menu=filemenu)

        def edit_configuration(parent, settings:Configuration):
            dialog_box = EditConfigurationDialog(parent, settings)
            parent.wait_window(dialog_box)
            settings.save()

        editmenu = tk.Menu(menu, tearoff=0)
        editmenu.add_command(label='Configuration', font=self.default_font,
                            command=partial(edit_configuration, self, self.settings))
        menu.add_cascade(label='Edit', font=self.default_font, menu=editmenu)

        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label='About', font=self.default_font)
        menu.add_cascade(label='Help', font=self.default_font, menu=helpmenu)

        self.config(menu=menu)

    def create_status_widget(self):
        status_row = ctk.CTkFrame(master=self)
        status_row.grid(column=0, row=0, padx=5, pady=5, sticky=tk.EW)

        self.status_indicator = ctk.CTkFrame(master=status_row, fg_color='yellow', width=28, height=28, corner_radius=0)
        self.status_indicator.grid(column=0, row=0, padx=0, pady=0)

        slot_label = ctk.CTkLabel(master=status_row, text='Slot:')
        slot_label.grid(column=1, row=0, padx=5, pady=0)

        slot_value = ctk.CTkLabel(master=status_row, textvariable=self.current_slot)
        slot_value.grid(column=2, row=0, padx=0, pady=0)

    def create_tab_views(self):
        tabview = ctk.CTkTabview(self)
        tabview.grid(column=0, row=1, padx=0, pady=0, sticky=tk.NSEW)

        wallets_tab = tabview.add("Wallets")
        wallets_tab.rowconfigure(index=0, weight=1)
        wallets_tab.columnconfigure(index=0, weight=1)

        policies_tab = tabview.add("Policies")
        policies_tab.rowconfigure(index=0, weight=1)
        policies_tab.columnconfigure(index=0, weight=1)

        projects_tab = tabview.add("Projects")
        projects_tab.rowconfigure(index=0, weight=1)
        projects_tab.columnconfigure(index=0, weight=1)

        tabview.set("Policies")

        self.wallets_frame = WalletsFrame(wallets_tab, self.settings, self.user, self.node)
        self.wallets_frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NSEW)

        self.policies_frame = PoliciesFrame(policies_tab, self.settings, self.user, self.node)
        self.policies_frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NSEW)

        #projects_frame = ProjectsFrame(policies_tab, self.settings, self.user)
        #projects_frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NSEW)


    def __init__(self, settings, user, node):
        super().__init__()

        self.settings = settings
        self.user = user
        self.node = node
        self.current_slot = tk.StringVar(value='00000000')
        self.status_indicator = None
        self.wallets_frame = None
        self.policies_frame = None
        self.projects_frame = None


        style = ttk.Style(self)
        style.theme_use("clam")
        self.default_font = tk.font.nametofont("TkDefaultFont")
        self.default_font.configure(family='lucida',
                                    size=26,
                                    weight=tk.font.NORMAL)
        style.configure("Treeview.Heading", font=self.default_font)
        style.configure('Treeview', rowheight=self.default_font.metrics('linespace')+2)

        self.option_add('*font', 'lucida 26')
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")
        self.geometry('1000x600')

        self.title('TCR: NFT Mint')
        self.create_menu()
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=0)
        self.rowconfigure(index=1, weight=1)
        self.create_status_widget()
        self.create_tab_views()

    def update_status(self, healthy:bool, slot:int):
        if healthy:
            self.status_indicator.configure(fg_color='green')
        else:
            self.status_indicator.configure(fg_color='red')

        self.current_slot.set(f'{slot}')
        self.policies_frame.update_current_slot(slot)
