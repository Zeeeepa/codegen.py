"""
Login frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from typing import Any

from codegen_ui.utils.constants import PADDING


class LoginFrame(ttk.Frame):
    """
    Login frame for the Codegen UI.
    
    This frame allows users to log in to the Codegen API.
    """
    
    def __init__(self, parent: Any, app: Any):
        """
        Initialize the login frame.
        
        Args:
            parent: Parent widget
            app: Application instance
        """
        super().__init__(parent)
        self.app = app
        
        # Create variables
        self.api_key_var = tk.StringVar()
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the login frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=PADDING*2, pady=PADDING*2)
        
        # Create header
        header = ttk.Label(
            container, 
            text="Login to Codegen", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, PADDING*2))
        
        # Create form
        form = ttk.Frame(container)
        form.pack(fill=tk.BOTH, expand=True)
        
        # API key label
        api_key_label = ttk.Label(form, text="API Key:")
        api_key_label.grid(row=0, column=0, sticky=tk.W, pady=PADDING)
        
        # API key entry
        api_key_entry = ttk.Entry(form, textvariable=self.api_key_var, width=50, show="*")
        api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=PADDING)
        
        # Show/hide API key
        self.show_api_key_var = tk.BooleanVar(value=False)
        show_api_key_cb = ttk.Checkbutton(
            form, 
            text="Show API Key", 
            variable=self.show_api_key_var,
            command=self._toggle_api_key_visibility
        )
        show_api_key_cb.grid(row=1, column=1, sticky=tk.W, pady=PADDING)
        
        # Login button
        login_button = ttk.Button(
            form, 
            text="Login", 
            command=self._login
        )
        login_button.grid(row=2, column=1, sticky=tk.W, pady=PADDING*2)
        
        # Get API key link
        get_api_key_link = ttk.Label(
            form, 
            text="Don't have an API key? Get one here", 
            foreground="blue", 
            cursor="hand2"
        )
        get_api_key_link.grid(row=3, column=1, sticky=tk.W, pady=PADDING)
        get_api_key_link.bind("<Button-1>", self._open_api_key_page)
        
        # Configure grid
        form.columnconfigure(1, weight=1)
        
    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        show = self.show_api_key_var.get()
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Entry) and grandchild.cget("textvariable") == str(self.api_key_var):
                        grandchild.config(show="" if show else "*")
                        break
        
    def _login(self):
        """Handle login button click."""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self.app.set_status("API key is required")
            return
            
        self.app.login(api_key)
        
    def _open_api_key_page(self, event):
        """Open the API key page in a web browser."""
        webbrowser.open("https://codegen.com/settings")

