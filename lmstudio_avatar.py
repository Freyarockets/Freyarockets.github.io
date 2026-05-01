#!/usr/bin/env python3
"""
LM Studio Avatar - A tkinter GUI for interacting with LM Studio localhost instance
Requires: requests, tkinter (built-in)
Install: pip install requests
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import requests
import threading
from datetime import datetime
import json

class LMStudioAvatar:
    def __init__(self, root):
        self.root = root
        self.root.title("LM Studio Avatar")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configuration
        self.lm_studio_url = "http://localhost:1234/v1/chat/completions"
        self.is_loading = False
        
        # Create GUI
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # --- Header Section ---
        header_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="LM Studio URL:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.url_entry = ttk.Entry(header_frame, width=50)
        self.url_entry.insert(0, self.lm_studio_url)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(header_frame, text="Model:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.model_entry = ttk.Entry(header_frame, width=20)
        self.model_entry.insert(0, "gpt-3.5-turbo")
        self.model_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(header_frame, text="Test Connection", command=self.test_connection).grid(
            row=0, column=4, padx=5
        )
        
        # Temperature and Max Tokens
        param_frame = ttk.Frame(header_frame)
        param_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(param_frame, text="Temperature:").pack(side=tk.LEFT, padx=5)
        self.temperature_var = tk.DoubleVar(value=0.7)
        temp_spin = ttk.Spinbox(param_frame, from_=0.0, to=2.0, increment=0.1, 
                                textvariable=self.temperature_var, width=5)
        temp_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(param_frame, text="Max Tokens:").pack(side=tk.LEFT, padx=5)
        self.max_tokens_var = tk.IntVar(value=512)
        tokens_spin = ttk.Spinbox(param_frame, from_=1, to=4096, increment=100,
                                  textvariable=self.max_tokens_var, width=5)
        tokens_spin.pack(side=tk.LEFT, padx=5)
        
        # --- Conversation Display ---
        display_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="10")
        display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        self.conversation_display = scrolledtext.ScrolledText(
            display_frame, height=15, width=100, wrap=tk.WORD, state=tk.DISABLED
        )
        self.conversation_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for styling
        self.conversation_display.tag_config("user", foreground="#0066cc", font=("Arial", 10, "bold"))
        self.conversation_display.tag_config("assistant", foreground="#006600", font=("Arial", 10))
        self.conversation_display.tag_config("system", foreground="#cc6600", font=("Arial", 9, "italic"))
        self.conversation_display.tag_config("timestamp", foreground="#999999", font=("Arial", 8))
        
        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Your Query", padding="10")
        input_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.query_input = scrolledtext.ScrolledText(
            input_frame, height=4, width=100, wrap=tk.WORD
        )
        self.query_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # --- Button Section ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        self.send_button = ttk.Button(button_frame, text="Send Query", command=self.send_query)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Conversation", command=self.clear_conversation).pack(
            side=tk.LEFT, padx=5
        )
        
        ttk.Button(button_frame, text="Save Conversation", command=self.save_conversation).pack(
            side=tk.LEFT, padx=5
        )
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def test_connection(self):
        """Test connection to LM Studio"""
        self.status_var.set("Testing connection...")
        self.root.update()
        
        try:
            url = self.url_entry.get()
            response = requests.post(
                url,
                json={
                    "model": self.model_entry.get(),
                    "messages": [{"role": "user", "content": "Hello"}],
                    "temperature": 0.7,
                    "max_tokens": 10
                },
                timeout=5
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Connected to LM Studio successfully!")
                self.status_var.set("Connected ✓")
            else:
                messagebox.showerror("Error", f"Server returned status code: {response.status_code}")
                self.status_var.set("Connection failed")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Could not connect to LM Studio.\nMake sure it's running on localhost:1234")
            self.status_var.set("Connection failed")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            self.status_var.set("Connection failed")
    
    def send_query(self):
        """Send query to LM Studio in a separate thread"""
        query = self.query_input.get("1.0", tk.END).strip()
        
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a query")
            return
        
        if self.is_loading:
            messagebox.showwarning("Busy", "Already processing a query")
            return
        
        # Disable send button and start thread
        self.send_button.config(state=tk.DISABLED)
        self.is_loading = True
        self.query_input.config(state=tk.DISABLED)
        
        # Add user message to display
        self.add_message("user", query)
        self.query_input.delete("1.0", tk.END)
        
        # Start query in separate thread
        thread = threading.Thread(target=self._send_query_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _send_query_thread(self, query):
        """Send query in background thread"""
        try:
            self.status_var.set("Waiting for response...")
            self.root.update()
            
            url = self.url_entry.get()
            model = self.model_entry.get()
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": query}],
                "temperature": self.temperature_var.get(),
                "max_tokens": self.max_tokens_var.get(),
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    assistant_message = data["choices"][0]["message"]["content"]
                    self.add_message("assistant", assistant_message)
                    self.status_var.set("Response received ✓")
                else:
                    self.add_message("system", "Error: No response from model")
                    self.status_var.set("Error: No response")
            else:
                error_msg = f"Error: Server returned status {response.status_code}\n{response.text}"
                self.add_message("system", error_msg)
                self.status_var.set(f"Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.add_message("system", "Error: Request timed out")
            self.status_var.set("Error: Timeout")
        except requests.exceptions.ConnectionError:
            self.add_message("system", "Error: Could not connect to LM Studio")
            self.status_var.set("Error: Connection failed")
        except Exception as e:
            self.add_message("system", f"Error: {str(e)}")
            self.status_var.set("Error")
        
        finally:
            # Re-enable send button
            self.send_button.config(state=tk.NORMAL)
            self.query_input.config(state=tk.NORMAL)
            self.is_loading = False
            self.query_input.focus()
    
    def add_message(self, role, content):
        """Add a message to the conversation display"""
        self.conversation_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add timestamp
        self.conversation_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add role and content
        if role == "user":
            self.conversation_display.insert(tk.END, "You: ", "user")
        elif role == "assistant":
            self.conversation_display.insert(tk.END, "Assistant: ", "assistant")
        else:
            self.conversation_display.insert(tk.END, "System: ", "system")
        
        self.conversation_display.insert(tk.END, f"{content}\n\n")
        
        # Scroll to bottom
        self.conversation_display.see(tk.END)
        self.conversation_display.config(state=tk.DISABLED)
    
    def clear_conversation(self):
        """Clear the conversation display"""
        if messagebox.askyesno("Clear", "Clear all conversation history?"):
            self.conversation_display.config(state=tk.NORMAL)
            self.conversation_display.delete("1.0", tk.END)
            self.conversation_display.config(state=tk.DISABLED)
    
    def save_conversation(self):
        """Save conversation to a file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    content = self.conversation_display.get("1.0", tk.END)
                    f.write(content)
                messagebox.showinfo("Success", f"Conversation saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_settings(self):
        """Load saved settings (placeholder for future enhancement)"""
        try:
            with open("lmstudio_settings.json", "r") as f:
                settings = json.load(f)
                if "url" in settings:
                    self.url_entry.delete(0, tk.END)
                    self.url_entry.insert(0, settings["url"])
                if "model" in settings:
                    self.model_entry.delete(0, tk.END)
                    self.model_entry.insert(0, settings["model"])
        except FileNotFoundError:
            pass
    
    def save_settings(self):
        """Save settings for next session"""
        settings = {
            "url": self.url_entry.get(),
            "model": self.model_entry.get()
        }
        try:
            with open("lmstudio_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LMStudioAvatar(root)
    
    # Save settings on exit
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
