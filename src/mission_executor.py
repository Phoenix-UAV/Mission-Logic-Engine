"""File containing the definition of the MissionRunner class."""
from enum import Enum, auto
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
import importlib.util
import datetime
from types import ModuleType
from typing import final

def void(_) -> None:
    """Consume a return value"""

class Node:
    """Node for the mission executor."""
    def __init__(self, data):
        self.id: int = data["id"] or -1
        self.name: str = data["name"]
        self.position: list[int] = [data.get("x", 0), data.get("y", 0)]
        self.code_file: str = data["code_file"]
        self.connections: dict[int, int] = data.get("connections", {})  # int -> node_id
        self.module: ModuleType
        self.code: str = "return -1\n" # Return generic error code -1

    def load_code(self, mission_folder: str):
        """Load code from the mission folder."""
        filepath = os.path.join(mission_folder, self.code_file)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="UTF-8") as f:
                self.code = f.read()
        else:
            self.code = "# Missing code file\n return -1\n"

    def import_module(self, mission_folder: str) -> bool:
        """Import a module from the mission folder."""
        # Add mission folder to sys.path temporarily
        if mission_folder not in sys.path:
            sys.path.insert(0, mission_folder)
        try:
            spec = importlib.util.spec_from_file_location(
                self.name,
                os.path.join(mission_folder, self.code_file)
            )
            if spec is None:
                return False
            self.module = importlib.util.module_from_spec(spec)
            if spec.loader:
                spec.loader.exec_module(self.module)
            return True
        except Exception as _e:
            return False

    def run(self) -> int:
        """Run the code on the node. Returns -1 if there is no code."""
        # Call run() function
        if hasattr(self.module, "run"):
            return self.module.run()
        return -1

class State(Enum):
    """Enum for the valid states"""
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    STEPPING = auto() # used when user clicks Step button
    PAUSED_STEP = auto()

@final
class MissionRunner:
    """Mission Runner app class."""
    def __init__(self, tk_root: tk.Tk):
        self.root: tk.Tk = tk_root
        self.root.title("Mission Runner")
        self.root.geometry("900x700")

        self.mission_filepath: str      = ""
        self.nodes: list[Node]          = []
        self.root_node_id: int          = -1
        self.current_node_id: int       = -1
        self.node_dict: dict[int, Node] = {}      # id -> Node

        self.state: State = State.STOPPED
        self.stop_requested: bool = False

        # Logging
        self.log_lines: list[str] = []
        self.log_file_path: str = ""

        self.logs_folder: str = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(self.logs_folder, exist_ok=True)

        # Build GUI
        self.build_widgets()

    def build_widgets(self):
        """Build the mission runner's widgets"""
        # Top: Load mission button and info
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            top_frame,
            text="Load Mission",
            command=self.load_mission
        ).pack(side=tk.LEFT, padx=5)
        self.mission_label: tk.Label = tk.Label(
            top_frame,
            text="No mission loaded",
            font=("Arial", 10, "bold")
        )
        self.mission_label.pack(side=tk.LEFT, padx=20)

        # Current node display
        current_frame = tk.LabelFrame(self.root, text="Current Node", padx=5, pady=5)
        current_frame.pack(fill=tk.X, padx=5, pady=5)

        self.current_node_label: tk.Label = tk.Label(current_frame, text="(none)",
                                                     font=("Arial", 12, "bold"))
        self.current_node_label.pack(side=tk.LEFT, padx=10)

        self.current_node_code: tk.Label = tk.Label(
            current_frame,
            text="",
            wraplength=400,
            justify=tk.LEFT
        )
        self.current_node_code.pack(side=tk.LEFT, padx=10)

        # Control buttons
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_btn: tk.Button = tk.Button(
            ctrl_frame,
            text="Start",
            command=self.start_mission,
            width=8
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn: tk.Button = tk.Button(
            ctrl_frame,
            text="Pause",
            command=self.toggle_pause,
            state=tk.DISABLED,
            width=8
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn: tk.Button = tk.Button(
            ctrl_frame,
            text="Stop",
            command=self.stop_mission,
            state=tk.DISABLED,
            width=8
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.step_btn: tk.Button = tk.Button(
            ctrl_frame,
            text="Step",
            command=self.step,
            state=tk.DISABLED, width=8
        )
        self.step_btn.pack(side=tk.LEFT, padx=5)

        self.pause_after_cb: tk.Checkbutton = tk.Checkbutton(
            ctrl_frame,
            text="Toggle Stepping",
            command=self.toggle_stepping
        )
        self.pause_after_cb.pack(side=tk.LEFT, padx=10)

        # Manual state set
        manual_frame = tk.Frame(self.root)
        manual_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(manual_frame, text="Set Current Node:").pack(side=tk.LEFT)
        self.node_dropdown_var: tk.StringVar = tk.StringVar()
        self.node_dropdown: ttk.Combobox = ttk.Combobox(
            manual_frame,
            textvariable=self.node_dropdown_var,
            state="readonly",
            width=20
        )
        self.node_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Button(
            manual_frame,
            text="Set",
            command=self.set_current_node
        ).pack(side=tk.LEFT, padx=5)

        # Log area
        log_frame = tk.LabelFrame(self.root, text="Log", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text: scrolledtext.ScrolledText = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # ---------- Mission Loading ----------
    def load_mission(self):
        """Load the current mission."""
        folder = filedialog.askdirectory(title="Select Mission Folder")
        if not folder:
            return

        meta_path = os.path.join(folder, "mission.json")
        if not os.path.exists(meta_path):
            void(messagebox.showerror("Error", "mission.json not found."))
            return

        try:
            with open(meta_path, "r", encoding="UTF-8") as f:
                meta = json.load(f)
        except OSError as e:
            void(messagebox.showerror("Error", f"Failed to load mission: {e}"))
            return

        self.mission_filepath = folder
        mission_name = os.path.basename(self.mission_filepath)
        void(self.mission_label.config(text=f"Mission: {mission_name}"))

        # Build nodes
        self.nodes = []
        self.node_dict = {}
        for data in meta["nodes"]:
            node = Node(data)
            node.load_code(folder)
            self.nodes.append(node)
            self.node_dict[node.id] = node

        self.root_node_id = meta.get("root_id") or -1
        if self.root_node_id == -1 and self.nodes:
            self.root_node_id = self.nodes[0].id

        # Update dropdown
        self.node_dropdown['values'] = [f"{n.id}: {n.name}" for n in self.nodes]
        if self.root_node_id in self.node_dict:
            self.current_node_id = self.root_node_id
            self.node_dropdown_var.set(f"{self.current_node_id}: {\
                self.node_dict[self.current_node_id].name}")

        # Reset state
        self.stop_mission()
        self.log_text.delete(1.0, tk.END)
        self.log_lines = []
        self.log(f"Mission loaded: {mission_name}")

        # Import all node modules (pre-load)
        for node in self.nodes:
            success = node.import_module(folder)
            if not success:
                self.log(f"Warning: Failed to import node {node.name}")

        self.update_current_node_display()

    # ---------- Logging ----------
    def log(self, message: str):
        """Add a message to the log."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        self.log_lines.append(line)
        self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def flush_log_to_file(self):
        """Empty the log buffer to the log file."""
        if not self.log_lines or self.mission_filepath == "":
            return

        # Prepare filename
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{os.path.basename(self.mission_filepath)}_{dt}_log.txt"
        filepath = os.path.join(self.logs_folder, filename)
        try:
            with open(filepath, "w", encoding="UTF-8") as f:
                void(f.write("\n".join(self.log_lines)))
            self.log_file_path = filepath
            self.log(f"Log saved to {filepath}")
        except OSError as e:
            self.log(f"Failed to save log: {e}")

    # ---------- Runner Control ----------
    def start_mission(self):
        """Start the current mission."""
        if self.state == State.RUNNING:
            return
        if not self.nodes:
            void(messagebox.showwarning("No mission", "Load a mission first."))
            return

        # Reset logs if restarting
        if not self.log_lines:
            self.log_text.delete(1.0, tk.END)

        self.state = State.RUNNING
        self.stop_requested = False

        # Enable/disable buttons
        void(self.start_btn.config(     state=tk.DISABLED))
        void(self.pause_btn.config(     state=tk.NORMAL, text="Pause"))
        void(self.stop_btn.config(      state=tk.NORMAL))
        void(self.step_btn.config(      state=tk.NORMAL))
        void(self.pause_after_cb.config(state=tk.NORMAL))
        void(self.node_dropdown.config( state=tk.DISABLED))

        # Start from root or current node
        if self.current_node_id == -1:
            self.current_node_id = self.root_node_id
        if self.current_node_id == -1:
            self.log("Error: No root node defined.")
            self.stop_mission()
            return

        self.log(f"Mission started from node {self.current_node_id}")
        # Run first node immediately
        self.run_current_node()

    def toggle_pause(self):
        """Pause or unpause the mission runner."""
        match self.state:
            case State.RUNNING:
                self.state = State.PAUSED
                self.log("Paused")
                void(self.pause_btn.config(text="Resume"))
                return

            case State.PAUSED:
                self.state = State.RUNNING
                self.log("Resumed")
                void(self.pause_btn.config(text="Pause"))
                self.run_current_node()
                return

            case State.STEPPING:
                self.state = State.PAUSED_STEP
                self.log("Paused stepping")
                void(self.pause_btn.config(text="Resume"))
                return

            case State.PAUSED_STEP:
                self.state = State.STEPPING
                self.log("Resumed stepping")
                void(self.pause_btn.config(text="Pause"))
                return

            case State.STOPPED:
                return

    def stop_mission(self):
        """Stop the current mission."""
        # Reset buttons
        void(self.start_btn.config(     state=tk.NORMAL))
        void(self.pause_btn.config(     state=tk.DISABLED, text="Pause"))
        void(self.stop_btn.config(      state=tk.DISABLED))
        void(self.step_btn.config(      state=tk.DISABLED))
        void(self.pause_after_cb.config(state=tk.NORMAL))
        void(self.node_dropdown.config( state="readonly"))
        self.log("Mission stopped")
        self.state = State.STOPPED
        self.stop_requested = True

    def step(self):
        """Step the runner by one instruction."""
        if self.state == State.STOPPED:
            # If stopped, start in step mode
            if not self.nodes:
                void(messagebox.showwarning("No mission", "Load a mission first."))
                return
            self.start_mission()
            # After start, we are in running state; set step mode and pause
            self.state = State.PAUSED_STEP
            void(self.pause_btn.config(text="Resume"))
            self.log("Step mode: will run one node then pause.")
            # The first node will be executed by start, but we need to ensure pause after it.
            # Actually start calls run_current_node() which will check pause after node.
            # We'll set pause_after_node to True for this step? Better:
            # run_current_node will check self.step_mode.
            return

        self.state = State.STEPPING
        void(self.pause_btn.config(text="Pause"))
        self.run_current_node()

    def toggle_stepping(self):
        """Toggle whether to pause after each node processing."""
        match self.state:
            case State.RUNNING:
                self.state = State.STEPPING
                self.log("Enabled stepping")
                return

            case State.PAUSED:
                self.state = State.PAUSED_STEP
                self.log("Enabled stepping")
                return

            case State.STEPPING:
                self.state = State.RUNNING
                self.log("Disabled stepping")
                return

            case State.PAUSED_STEP:
                self.state = State.PAUSED
                self.log("Disabled stepping")
                return

            case State.STOPPED:
                return

    def set_current_node(self):
        """Set the current node."""
        if self.state == State.RUNNING:
            void(messagebox.showinfo(
                "Cannot change",
                "Stop or pause the mission before changing current node."
            ))
            return
        val = self.node_dropdown_var.get()
        if not val:
            return

        nid = int(val.split(":")[0])
        if nid in self.node_dict:
            self.current_node_id = nid
            self.update_current_node_display()
            self.log(f"Manually set current node to {self.node_dict[nid].name}")
        else:
            void(messagebox.showerror("Error", "Invalid node."))

    # ---------- Core Execution ----------
    def run_current_node(self):
        """Run the currently selected node."""
        if self.state not in [State.RUNNING, State.STEPPING] or self.stop_requested:
            return

        if self.current_node_id not in self.node_dict:
            self.log("Error: Current node not found.")
            self.stop_mission()
            return

        node = self.node_dict[self.current_node_id]

        # Update display
        self.update_current_node_display()

        # Execute the node's run()
        self.log(f"Executing node: {node.name} (ID: {node.id})")
        try:
            result = node.run()
            self.log(f"Node returned: {result}")
        except Exception as e:
            self.log(f"Failed to run node: {e}")
            self.stop_mission()
            return

        # Determine next node
        if result not in node.connections:
            self.log(f"No transition for return value {result}. Stopping.")
            self.stop_mission()
            return

        next_node_id: int = node.connections[result]
        next_node = self.node_dict[next_node_id]
        if next_node.id == -1:
            self.log(f"Target node {next_node_id} not found. Stopping.")
            self.stop_mission()
            return

        self.log(f"Transitioning to node: {next_node.name} (ID: {next_node.id})")
        self.current_node_id = next_node_id
        self.node_dropdown_var.set(f"{next_node.id}: {next_node.name}")

        # Check pause after node
        if self.state == State.STEPPING:
            void(self.pause_btn.config(text="Resume"))
            self.log("Paused after node (step or auto-pause).")
            return

        # Continue to next node (immediate)
        # Use after to avoid recursion and keep GUI responsive
        void(self.root.after(10, self.run_current_node))

    def update_current_node_display(self):
        """Update the selected node's display properties"""
        node = self.node_dict.get(self.current_node_id)
        if node:
            void(self.current_node_label.config(text=f"{node.name} (ID: {node.id})"))
            # Show first few lines of code
            code_preview = node.code.split("\n")[:5]
            preview = "\n".join(code_preview)
            if len(node.code.split("\n")) > 5:
                preview += "\n..."
            void(self.current_node_code.config(text=preview))
        else:
            void(self.current_node_label.config(text="(none)"))
            void(self.current_node_code.config(text=""))

    # ---------- Cleanup ----------
    def on_closing(self):
        """Run this method when the app is closed."""
        if self.state == State.RUNNING:
            self.stop_mission()
        self.flush_log_to_file()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MissionRunner(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
