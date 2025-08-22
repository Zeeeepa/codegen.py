"""
Main application module for the Codegen UI.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import json
from typing import Dict, List, Optional, Any, Callable

from codegen_client import CodegenClient, CodegenApiError
from codegen_ui.components.login_frame import LoginFrame
from codegen_ui.components.agent_list_frame import AgentListFrame
from codegen_ui.components.project_frame import ProjectFrame
from codegen_ui.components.agent_detail_frame import AgentDetailFrame
from codegen_ui.components.create_agent_frame import CreateAgentFrame
from codegen_ui.utils.config import Config
from codegen_ui.utils.constants import THEME, PADDING


class CodegenApp:
    """
    Main application class for the Codegen UI.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the Codegen UI application.

        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Codegen UI")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set theme
        self._apply_theme()
        
        # Initialize config
        self.config = Config()
        
        # Initialize client
        self.client = None
        self.current_org_id = None
        
        # Create message queue for thread-safe UI updates
        self.message_queue = queue.Queue()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Initialize UI components
        self._init_ui()
        
        # Start message processing
        self._process_messages()
        
        # Check if we have a saved API key
        self._check_saved_credentials()

    def _apply_theme(self):
        """Apply the application theme."""
        style = ttk.Style()
        style.theme_use(THEME)
        
        # Configure styles
        style.configure("TFrame", background=self.root.cget("background"))
        style.configure("TLabel", background=self.root.cget("background"))
        style.configure("TButton", padding=5)
        style.configure("TNotebook", padding=5)
        style.configure("TNotebook.Tab", padding=[10, 5])
        
        # Custom styles
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Subheader.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Status.TLabel", font=("Helvetica", 10, "italic"))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
        style.configure("Warning.TLabel", foreground="orange")
        style.configure("Info.TLabel", foreground="blue")

    def _init_ui(self):
        """Initialize the UI components."""
        # Create the notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        
        # Create frames for each tab
        self.login_frame = LoginFrame(self.notebook, self)
        self.agent_list_frame = AgentListFrame(self.notebook, self)
        self.project_frame = ProjectFrame(self.notebook, self)
        self.create_agent_frame = CreateAgentFrame(self.notebook, self)
        
        # Add frames to notebook
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.agent_list_frame, text="Agent Runs")
        self.notebook.add(self.project_frame, text="Projects")
        self.notebook.add(self.create_agent_frame, text="Create Agent")
        
        # Disable tabs until logged in
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.tab(3, state="disabled")
        
        # Pack the notebook
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.main_container, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(PADDING, 0))
        
        # Create agent detail frame (not in notebook)
        self.agent_detail_frame = AgentDetailFrame(self.main_container, self)
        
        # Create menu
        self._create_menu()

    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Login", command=self._show_login)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Agent Runs", command=lambda: self._show_tab(1))
        view_menu.add_command(label="Projects", command=lambda: self._show_tab(2))
        view_menu.add_command(label="Create Agent", command=lambda: self._show_tab(3))
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self.refresh_current_tab)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._open_documentation)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def _check_saved_credentials(self):
        """Check if we have saved credentials and log in automatically."""
        api_key = self.config.get("api_key")
        if api_key:
            self.login_frame.api_key_var.set(api_key)
            self.login(api_key)

    def _show_login(self):
        """Show the login tab."""
        self.notebook.select(0)

    def _show_tab(self, tab_index: int):
        """
        Show a specific tab.
        
        Args:
            tab_index: Index of the tab to show
        """
        if self.notebook.tab(tab_index, "state") != "disabled":
            self.notebook.select(tab_index)

    def _show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About Codegen UI",
            "Codegen UI v0.1.0\n\nA Tkinter-based GUI for the Codegen API."
        )

    def _open_documentation(self):
        """Open the documentation in a web browser."""
        import webbrowser
        webbrowser.open("https://docs.codegen.com/api-reference")

    def login(self, api_key: str):
        """
        Log in to the Codegen API.
        
        Args:
            api_key: API key for authentication
        """
        self.set_status("Logging in...")
        
        def _login_thread():
            try:
                # Initialize client
                self.client = CodegenClient(api_key=api_key)
                
                # Test connection by getting organizations
                orgs = self.client.organizations.get_organizations()
                
                # Save API key
                self.config.set("api_key", api_key)
                
                # Set current organization
                if orgs.items:
                    self.current_org_id = orgs.items[0].id
                
                # Enable tabs
                self.message_queue.put(("enable_tabs", None))
                
                # Update status
                self.message_queue.put(("set_status", f"Logged in. Found {orgs.total} organizations."))
                
                # Load data
                self.message_queue.put(("load_data", None))
                
            except Exception as e:
                self.message_queue.put(("login_error", str(e)))
        
        # Start login thread
        threading.Thread(target=_login_thread, daemon=True).start()

    def logout(self):
        """Log out from the Codegen API."""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            # Clear API key
            self.config.set("api_key", "")
            
            # Disable tabs
            self.notebook.tab(1, state="disabled")
            self.notebook.tab(2, state="disabled")
            self.notebook.tab(3, state="disabled")
            
            # Show login tab
            self.notebook.select(0)
            
            # Clear client
            self.client = None
            self.current_org_id = None
            
            # Update status
            self.set_status("Logged out")
            
            # Clear data
            self.agent_list_frame.clear()
            self.project_frame.clear()
            self.create_agent_frame.clear()

    def refresh_current_tab(self):
        """Refresh the current tab."""
        current_tab = self.notebook.index("current")
        
        if current_tab == 1:  # Agent Runs
            self.agent_list_frame.load_agent_runs()
        elif current_tab == 2:  # Projects
            self.project_frame.load_projects()

    def set_status(self, message: str):
        """
        Set the status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_var.set(message)
        self.root.update_idletasks()

    def show_agent_detail(self, agent_run_id: str):
        """
        Show the agent detail frame.
        
        Args:
            agent_run_id: ID of the agent run to display
        """
        # Hide notebook
        self.notebook.pack_forget()
        
        # Show agent detail frame
        self.agent_detail_frame.load_agent_run(agent_run_id)
        self.agent_detail_frame.pack(fill=tk.BOTH, expand=True)

    def hide_agent_detail(self):
        """Hide the agent detail frame and show the notebook."""
        # Hide agent detail frame
        self.agent_detail_frame.pack_forget()
        
        # Show notebook
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def _process_messages(self):
        """Process messages from the message queue."""
        try:
            while not self.message_queue.empty():
                message, data = self.message_queue.get_nowait()
                
                if message == "set_status":
                    self.set_status(data)
                elif message == "login_error":
                    self.set_status("Login failed")
                    messagebox.showerror("Login Error", f"Failed to log in: {data}")
                elif message == "enable_tabs":
                    self.notebook.tab(1, state="normal")
                    self.notebook.tab(2, state="normal")
                    self.notebook.tab(3, state="normal")
                    self.notebook.select(1)  # Show Agent Runs tab
                elif message == "load_data":
                    self.agent_list_frame.load_agent_runs()
                    self.project_frame.load_projects()
                    self.create_agent_frame.load_models()
                
                self.message_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Schedule to run again
            self.root.after(100, self._process_messages)


def main():
    """Run the Codegen UI application."""
    root = tk.Tk()
    app = CodegenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

