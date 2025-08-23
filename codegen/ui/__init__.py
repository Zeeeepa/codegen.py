"""
Codegen UI module.

This module provides a simple UI for the Codegen API.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox

class CodegenTkApp:
    """
    A simple Tkinter-based UI for the Codegen API.
    """
    
    def __init__(self, root):
        """
        Initialize the Codegen UI.
        
        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the title label
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Codegen UI", 
            font=("Helvetica", 16)
        )
        self.title_label.pack(pady=10)
        
        # Create the API key entry
        self.api_key_frame = ttk.Frame(self.main_frame)
        self.api_key_frame.pack(fill=tk.X, pady=10)
        
        self.api_key_label = ttk.Label(
            self.api_key_frame, 
            text="API Key:"
        )
        self.api_key_label.pack(side=tk.LEFT, padx=5)
        
        self.api_key_entry = ttk.Entry(
            self.api_key_frame, 
            width=50
        )
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        
        self.api_key_button = ttk.Button(
            self.api_key_frame, 
            text="Save",
            command=self.save_api_key
        )
        self.api_key_button.pack(side=tk.LEFT, padx=5)
        
        # Create the agent list
        self.agent_list_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Agent Runs"
        )
        self.agent_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.agent_list = ttk.Treeview(
            self.agent_list_frame,
            columns=("id", "status", "created_at"),
            show="headings"
        )
        self.agent_list.heading("id", text="ID")
        self.agent_list.heading("status", text="Status")
        self.agent_list.heading("created_at", text="Created At")
        self.agent_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the refresh button
        self.refresh_button = ttk.Button(
            self.agent_list_frame, 
            text="Refresh",
            command=self.refresh_agent_list
        )
        self.refresh_button.pack(pady=5)
        
        # Create the prompt entry
        self.prompt_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Create Agent Run"
        )
        self.prompt_frame.pack(fill=tk.X, pady=10)
        
        self.prompt_label = ttk.Label(
            self.prompt_frame, 
            text="Prompt:"
        )
        self.prompt_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.prompt_text = tk.Text(
            self.prompt_frame, 
            height=5
        )
        self.prompt_text.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_button = ttk.Button(
            self.prompt_frame, 
            text="Create Agent Run",
            command=self.create_agent_run
        )
        self.create_button.pack(pady=5)
        
        # Initialize the UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI with saved settings."""
        # Load the API key from settings
        try:
            from backend.core.config.client_config import ClientConfig
            config = ClientConfig()
            api_key = config.api_token
            if api_key:
                self.api_key_entry.insert(0, api_key)
        except ImportError:
            logging.warning("Failed to import ClientConfig. Using default settings.")
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
    
    def save_api_key(self):
        """Save the API key to settings."""
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("Error", "API key cannot be empty.")
            return
        
        try:
            from backend.core.config.client_config import ClientConfig
            config = ClientConfig()
            config.api_token = api_key
            config.save()
            messagebox.showinfo("Success", "API key saved successfully.")
        except ImportError:
            logging.warning("Failed to import ClientConfig. Using default settings.")
            messagebox.showwarning("Warning", "Failed to save API key. ClientConfig not found.")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def refresh_agent_list(self):
        """Refresh the agent list."""
        # Clear the current list
        for item in self.agent_list.get_children():
            self.agent_list.delete(item)
        
        # Get the API key
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("Error", "API key cannot be empty.")
            return
        
        try:
            from backend.client.endpoints.agents import CodegenClient
            client = CodegenClient(ClientConfig(api_token=api_key))
            agent_runs = client.list_agent_runs()
            
            for run in agent_runs:
                self.agent_list.insert(
                    "", 
                    tk.END, 
                    values=(run.id, run.status, run.created_at)
                )
        except ImportError:
            logging.warning("Failed to import CodegenClient. Using mock data.")
            # Add some mock data
            self.agent_list.insert("", tk.END, values=("1", "completed", "2023-01-01"))
            self.agent_list.insert("", tk.END, values=("2", "running", "2023-01-02"))
            self.agent_list.insert("", tk.END, values=("3", "failed", "2023-01-03"))
        except Exception as e:
            logging.error(f"Error refreshing agent list: {e}")
            messagebox.showerror("Error", f"Failed to refresh agent list: {e}")
    
    def create_agent_run(self):
        """Create a new agent run."""
        # Get the API key
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("Error", "API key cannot be empty.")
            return
        
        # Get the prompt
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Prompt cannot be empty.")
            return
        
        try:
            from backend.client.endpoints.agents import CodegenClient
            client = CodegenClient(ClientConfig(api_token=api_key))
            agent_run = client.create_agent_run(prompt=prompt)
            
            messagebox.showinfo("Success", f"Agent run created successfully. ID: {agent_run.id}")
            self.refresh_agent_list()
        except ImportError:
            logging.warning("Failed to import CodegenClient. Using mock data.")
            messagebox.showinfo("Success", "Agent run created successfully. (Mock)")
        except Exception as e:
            logging.error(f"Error creating agent run: {e}")
            messagebox.showerror("Error", f"Failed to create agent run: {e}")


# For backward compatibility
class CodegenApp(CodegenTkApp):
    """Alias for CodegenTkApp for backward compatibility."""
    pass
