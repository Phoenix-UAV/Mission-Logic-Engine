import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
import importlib.util
import datetime
import threading
import time
import queue

class Node:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        self.code_file = data["code_file"]
        self.connections = data.get("connections", {})  # int -> node_id
        self.module = None
        self.code = ""

    def load_code(self, mission_folder):
        filepath = os.path.join(mission_folder, self.code_file)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                self.code = f.read()
        else:
            self.code = "# Missing code file"

    def import_module(self, mission_folder):
        # Add mission folder to sys.path temporarily
        sys.path.insert(0, mission_folder)
        try:
            spec = importlib.util.spec_from_file_location(self.name, os.path.join(mission_folder, self.code_file))
            if spec is None:
                return False
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
            return True
        except Exception as e:
            return False
        finally:
            if mission_folder in sys.path:
                sys.path.remove(mission_folder)

    def run(self):
        if self.module is None:
            raise RuntimeError("Module not loaded")
        # Call run() function
        if hasattr(self.module, "run"):
            return self.module.run()
        else:
            raise RuntimeError("Node has no run() function")

class MissionRunner:
    def __init__(self, root):
        self.root = root
        self.root.title("Mission Runner")
        self.root.geometry("900x700")

        self.mission_folder = None
        self.mission_name = None
        self.nodes = []          # list of Node objects
        self.root_node_id = None
        self.current_node_id = None
        self.node_dict = {}      # id -> Node

        # Runner state
        self.running = False
        self.paused = False
        self.stop_requested = False
        self.pause_after_node = False
        self.step_mode = False   # used when user clicks Step button

        # Logging
        self.log_lines = []
        self.log_file_path = None
        self.logs_folder = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(self.logs_folder, exist_ok=True)

        # Build GUI
        self.build_widgets()

    def build_widgets(self):
        # Top: Load mission button and info
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(top_frame, text="Load Mission", command=self.load_mission).pack(side=tk.LEFT, padx=5)
        self.mission_label = tk.Label(top_frame, text="No mission loaded", font=("Arial", 10, "bold"))
        self.mission_label.pack(side=tk.LEFT, padx=20)

        # Current node display
        current_frame = tk.LabelFrame(self.root, text="Current Node", padx=5, pady=5)
        current_frame.pack(fill=tk.X, padx=5, pady=5)

        self.current_node_label = tk.Label(current_frame, text="(none)", font=("Arial", 12, "bold"))
        self.current_node_label.pack(side=tk.LEFT, padx=10)

        self.current_node_code = tk.Label(current_frame, text="", wraplength=400, justify=tk.LEFT)
        self.current_node_code.pack(side=tk.LEFT, padx=10)

        # Control buttons
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_btn = tk.Button(ctrl_frame, text="Start", command=self.start_mission, width=8)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(ctrl_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED, width=8)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(ctrl_frame, text="Stop", command=self.stop_mission, state=tk.DISABLED, width=8)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.step_btn = tk.Button(ctrl_frame, text="Step", command=self.step, state=tk.DISABLED, width=8)
        self.step_btn.pack(side=tk.LEFT, padx=5)

        self.pause_after_var = tk.IntVar(value=0)
        self.pause_after_cb = tk.Checkbutton(ctrl_frame, text="Pause After Each Node",
                                             variable=self.pause_after_var,
                                             command=self.toggle_pause_after)
        self.pause_after_cb.pack(side=tk.LEFT, padx=10)

        # Manual state set
        manual_frame = tk.Frame(self.root)
        manual_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(manual_frame, text="Set Current Node:").pack(side=tk.LEFT)
        self.node_dropdown_var = tk.StringVar()
        self.node_dropdown = ttk.Combobox(manual_frame, textvariable=self.node_dropdown_var, state="readonly", width=20)
        self.node_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Button(manual_frame, text="Set", command=self.set_current_node).pack(side=tk.LEFT, padx=5)

        # Log area
        log_frame = tk.LabelFrame(self.root, text="Log", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # ---------- Mission Loading ----------
    def load_mission(self):
        folder = filedialog.askdirectory(title="Select Mission Folder")
        if not folder:
            return
        meta_path = os.path.join(folder, "mission.json")
        if not os.path.exists(meta_path):
            messagebox.showerror("Error", "mission.json not found.")
            return

        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load mission: {e}")
            return

        self.mission_folder = folder
        self.mission_name = os.path.basename(folder)
        self.mission_label.config(text=f"Mission: {self.mission_name}")

        # Build nodes
        self.nodes = []
        self.node_dict = {}
        for data in meta["nodes"]:
            node = Node(data)
            node.load_code(folder)
            self.nodes.append(node)
            self.node_dict[node.id] = node

        self.root_node_id = meta.get("root_id")
        if self.root_node_id is None and self.nodes:
            self.root_node_id = self.nodes[0].id

        # Update dropdown
        self.node_dropdown['values'] = [f"{n.id}: {n.name}" for n in self.nodes]
        if self.root_node_id in self.node_dict:
            self.current_node_id = self.root_node_id
            self.node_dropdown_var.set(f"{self.current_node_id}: {self.node_dict[self.current_node_id].name}")

        # Reset state
        self.stop_mission()
        self.log_text.delete(1.0, tk.END)
        self.log_lines = []
        self.log(f"Mission loaded: {self.mission_name}")

        # Import all node modules (pre-load)
        for node in self.nodes:
            success = node.import_module(folder)
            if not success:
                self.log(f"Warning: Failed to import node {node.name}")

        self.update_current_node_display()

    # ---------- Logging ----------
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        self.log_lines.append(line)
        self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def flush_log_to_file(self):
        if not self.log_lines:
            return
        # Prepare filename
        if self.mission_name is None:
            return
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.mission_name}_{dt}_log.txt"
        filepath = os.path.join(self.logs_folder, filename)
        try:
            with open(filepath, "w") as f:
                f.write("\n".join(self.log_lines))
            self.log_file_path = filepath
            self.log(f"Log saved to {filepath}")
        except Exception as e:
            self.log(f"Failed to save log: {e}")

    # ---------- Runner Control ----------
    def start_mission(self):
        if self.running:
            return
        if not self.nodes:
            messagebox.showwarning("No mission", "Load a mission first.")
            return

        # Reset logs if restarting
        if not self.log_lines:
            self.log_text.delete(1.0, tk.END)

        self.running = True
        self.paused = False
        self.stop_requested = False
        self.step_mode = False

        # Enable/disable buttons
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="Pause")
        self.stop_btn.config(state=tk.NORMAL)
        self.step_btn.config(state=tk.NORMAL)
        self.pause_after_cb.config(state=tk.NORMAL)
        self.node_dropdown.config(state=tk.DISABLED)

        # Start from root or current node
        if self.current_node_id is None:
            self.current_node_id = self.root_node_id
        if self.current_node_id is None:
            self.log("Error: No root node defined.")
            self.stop_mission()
            return

        self.log(f"Mission started from node {self.current_node_id}")
        # Run first node immediately
        self.run_current_node()

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")
        if self.paused:
            self.log("Paused")
        else:
            self.log("Resumed")
            # If paused and not in step mode, continue execution
            if not self.step_mode:
                self.run_current_node()

    def stop_mission(self):
        self.running = False
        self.paused = False
        self.stop_requested = True
        self.step_mode = False
        # Reset buttons
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause")
        self.stop_btn.config(state=tk.DISABLED)
        self.step_btn.config(state=tk.DISABLED)
        self.pause_after_cb.config(state=tk.NORMAL)
        self.node_dropdown.config(state="readonly")
        self.log("Mission stopped")

    def step(self):
        if not self.running:
            # If stopped, start in step mode
            if not self.nodes:
                messagebox.showwarning("No mission", "Load a mission first.")
                return
            self.start_mission()
            # After start, we are in running state; set step mode and pause
            self.step_mode = True
            self.paused = True
            self.pause_btn.config(text="Resume")
            self.log("Step mode: will run one node then pause.")
            # The first node will be executed by start, but we need to ensure pause after it.
            # Actually start calls run_current_node() which will check pause after node.
            # We'll set pause_after_node to True for this step? Better: run_current_node will check self.step_mode.
        else:
            # If running, just run next node if paused
            if self.paused:
                self.step_mode = True
                self.paused = False  # temporarily resume to run one
                self.pause_btn.config(text="Pause")
                self.run_current_node()
            else:
                self.log("Step only works when paused or stopped.")

    def toggle_pause_after(self):
        self.pause_after_node = bool(self.pause_after_var.get())
        self.log(f"Pause after each node: {self.pause_after_node}")

    def set_current_node(self):
        if self.running and not self.paused:
            messagebox.showinfo("Cannot change", "Stop or pause the mission before changing current node.")
            return
        val = self.node_dropdown_var.get()
        if not val:
            return
        try:
            nid = int(val.split(":")[0])
            if nid in self.node_dict:
                self.current_node_id = nid
                self.update_current_node_display()
                self.log(f"Manually set current node to {self.node_dict[nid].name}")
            else:
                messagebox.showerror("Error", "Invalid node.")
        except:
            messagebox.showerror("Error", "Invalid selection.")

    # ---------- Core Execution ----------
    def run_current_node(self):
        if not self.running or self.stop_requested:
            return
        if self.paused and not self.step_mode:
            return

        node = self.node_dict.get(self.current_node_id)
        if node is None:
            self.log("Error: Current node not found.")
            self.stop_mission()
            return

        # Update display
        self.update_current_node_display()

        # Execute the node's run()
        try:
            self.log(f"Executing node: {node.name} (ID: {node.id})")
            result = node.run()
            self.log(f"Node returned: {result}")
        except Exception as e:
            self.log(f"Exception in node {node.name}: {e}")
            self.stop_mission()
            return

        # Determine next node
        next_node_id = node.connections.get(result)
        if next_node_id is None:
            self.log(f"No transition for return value {result}. Stopping.")
            self.stop_mission()
            return

        next_node = self.node_dict.get(next_node_id)
        if next_node is None:
            self.log(f"Target node {next_node_id} not found. Stopping.")
            self.stop_mission()
            return

        self.log(f"Transitioning to node: {next_node.name} (ID: {next_node.id})")
        self.current_node_id = next_node_id
        self.node_dropdown_var.set(f"{next_node.id}: {next_node.name}")

        # Check pause after node
        if self.pause_after_node or self.step_mode:
            self.paused = True
            self.pause_btn.config(text="Resume")
            self.step_mode = False  # one step done
            self.log("Paused after node (step or auto-pause).")
            return

        # Continue to next node (immediate)
        # Use after to avoid recursion and keep GUI responsive
        self.root.after(10, self.run_current_node)

    def update_current_node_display(self):
        node = self.node_dict.get(self.current_node_id)
        if node:
            self.current_node_label.config(text=f"{node.name} (ID: {node.id})")
            # Show first few lines of code
            code_preview = node.code.split("\n")[:5]
            preview = "\n".join(code_preview)
            if len(node.code.split("\n")) > 5:
                preview += "\n..."
            self.current_node_code.config(text=preview)
        else:
            self.current_node_label.config(text="(none)")
            self.current_node_code.config(text="")

    # ---------- Cleanup ----------
    def on_closing(self):
        if self.running:
            self.stop_mission()
        self.flush_log_to_file()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MissionRunner(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()