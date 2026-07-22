"""File containing the MissionEditorApp class."""
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os
import json
import shutil

class Node:
    """Node class for the Mission Editor."""
    def __init__(self, node_id: int, name: str, x: int, y: int, is_root: bool = False):
        self.id: int = node_id
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.is_root: bool = is_root
        self.code: str = "def run():\n    # Return an integer based on conditions\n    return 0\n"
        self.connections: dict[int, int] = {}  # int -> target_node_id

class MissionEditorApp:
    """Mission editor app class."""
    def __init__(self, tk_root: tk.Tk):
        self.root: tk.Tk = tk_root
        self.root.title("Mission Definition Interface")
        self.nodes: list[Node] = []
        self.selected_node: Node | None = None
        self.drag_data: dict[str, int] = {"x": 0, "y": 0}
        self.next_id: int = 1
        self.mission_folder: str = ""

        # Menu
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Mission",          command=self.new_mission)
        file_menu.add_command(label="Save Mission to Disk", command=self.save_mission_to_disk)
        file_menu.add_command(label="Load Mission",         command=self.load_mission)
        menubar.add_cascade(label="File", menu=file_menu)
        _ = self.root.config(menu=menubar)

        # Canvas
        self.canvas: tk.Canvas = tk.Canvas(self.root, bg="#ffffff")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        _ = self.canvas.bind("<Double-Button-1>", self.create_node)
        _ = self.canvas.bind("<ButtonPress-1>",   self.on_press)
        _ = self.canvas.bind("<B1-Motion>",       self.on_drag)
        _ = self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Context Menu
        self.ctx_menu: tk.Menu = tk.Menu(self.root, tearoff=0)
        self.ctx_menu.add_command(label="Edit Code",          command=self.edit_node_code)
        self.ctx_menu.add_command(label="Define Transitions", command=self.define_transitions)
        self.ctx_menu.add_command(label="Set as Root",        command=self.set_root)
        _ = self.canvas.bind("<Button-3>", self.show_context_menu)

    def new_mission(self):
        """Create a new mission."""
        if self.nodes and not messagebox.askyesno("Confirm", "Clear current mission?"):
            return
        self.nodes = []
        self.selected_node = None
        self.next_id = 1
        self.mission_folder = ""
        self.canvas.delete("all")
        _ = messagebox.showinfo("New Mission", "Canvas cleared. Double-click to add nodes.")

    def create_node(self, event: tk.Event):
        """Create a node."""
        name = simpledialog.askstring("Node Name", "Enter node name:")
        if not name:
            return
        if any(n.name == name for n in self.nodes):
            if not messagebox.askyesno(
                "Duplicate Name",
                f"Node '{name}' already exists. Continue?"
            ):
                return

        nid = self.next_id
        self.next_id += 1
        is_root = len(self.nodes) == 0
        node = Node(nid, name, event.x, event.y, is_root)
        self.nodes.append(node)
        self.draw_node(node)
        self.update_all_arrows()
        self.select_node(node)

    def draw_node(self, node: Node):
        """Draw the specified node."""
        # Remove old canvas items for this node
        for item in self.canvas.find_withtag(f"node_{node.id}"):
            self.canvas.delete(item)

        w, h = 140, 50
        x0, y0 = node.x - w/2, node.y - h/2

        outline = "#ff0000" if node.is_root else "#0055aa"
        fill = "#ccffcc" if node.is_root else "#e6f3ff"
        rect_id = self.canvas.create_rectangle(x0, y0, x0+w, y0+h, fill=fill, outline=outline,
                                               width=3 if node.is_root else 2)
        text_id = self.canvas.create_text(node.x, node.y, text=node.name,
                                          anchor="center", font=("Arial", 10, "bold"))

        # Tags: common tag for the whole node, and a specific one for the rectangle
        self.canvas.addtag_withtag(f"node_{node.id}", rect_id)
        self.canvas.addtag_withtag(f"node_{node.id}", text_id)
        self.canvas.addtag_withtag(f"rect_{node.id}", rect_id)   # <-- new tag for rectangle only

        _ = self.canvas.tag_bind(rect_id, "<Button-1>", lambda e: self.select_node(node))
        _ = self.canvas.tag_bind(text_id, "<Button-1>", lambda e: self.select_node(node))

    def select_node(self, node: Node):
        """Select the specified node."""
        # Deselect previous node – only change the rectangle
        if self.selected_node:
            rect_items = self.canvas.find_withtag(f"rect_{self.selected_node.id}")
            for item in rect_items:
                outline = "#ff0000" if self.selected_node.is_root else "#0055aa"
                width = 3 if self.selected_node.is_root else 2
                _ = self.canvas.itemconfig(item, outline=outline, width=width)
        self.selected_node = node
        if node:
            rect_items = self.canvas.find_withtag(f"rect_{node.id}")
            for item in rect_items:
                _ = self.canvas.itemconfig(item, outline="red", width=3)

    def on_press(self, event: tk.Event):
        """Run this code on press."""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event: tk.Event):
        """Run this code on drag."""
        if not self.selected_node:
            return
        dx: int = event.x - self.drag_data["x"]
        dy: int = event.y - self.drag_data["y"]
        self.selected_node.x += dx
        self.selected_node.y += dy
        self.draw_node(self.selected_node)
        self.update_all_arrows()
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event: tk.Event):
        """Run this code on release."""

    def show_context_menu(self, event: tk.Event):
        """Show the context menu."""
        # Find node under cursor
        items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("node_"):
                    nid = int(tag.split("_")[1])
                    node = next((n for n in self.nodes if n.id == nid), None)
                    if node:
                        self.select_node(node)
                        break
            if self.selected_node:
                break
        if self.selected_node:
            self.ctx_menu.tk_popup(event.x_root, event.y_root)

    def edit_node_code(self):
        """Edit the code in the selected node."""
        if not self.selected_node:
            _ = messagebox.showwarning("No Node", "Select a node first.")
            return

        editor = tk.Toplevel(self.root)
        editor.title(f"Edit Code: {self.selected_node.name}")
        editor.geometry("600x450")

        text = tk.Text(editor, wrap="none", font=("Consolas", 12))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", self.selected_node.code)

        def save_code():
            if self.selected_node is None:
                return
            self.selected_node.code = text.get("1.0", "end-1c")
            editor.destroy()

        btn = tk.Button(editor, text="Save Code", command=save_code)
        btn.pack(pady=5)

    def define_transitions(self):
        """Define transitions for the selected node."""
        if not self.selected_node:
            _ = messagebox.showwarning("No Node", "Select a node first.")
            return

        node = self.selected_node
        trans_win = tk.Toplevel(self.root)
        trans_win.title(f"Transitions for {node.name}")

        listbox = tk.Listbox(trans_win, width=60, height=10)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        def refresh_list():
            listbox.delete(0, tk.END)
            for val, target_id in node.connections.items():
                target = next((n for n in self.nodes if n.id == target_id), None)
                if target:
                    listbox.insert(tk.END, f"Return {val} -> {target.name}")
                else:
                    listbox.insert(tk.END, f"Return {val} -> [missing node]")

        refresh_list()

        def add_transition():
            try:
                ret_val = int(simpledialog.askstring(
                    "Transition",
                    "Integer return value from code:"
                ))
                target_names = [n.name for n in self.nodes if n.id != node.id]
                if not target_names:
                    _ = messagebox.showerror("Error", "No other nodes to connect to.")
                    return
                target_name = simpledialog.askstring(
                    "Target",
                    f"Select target node:\n{', '.join(target_names)}"
                )
                target_node = next((n for n in self.nodes if n.name == target_name), None)
                if target_node:
                    node.connections[ret_val] = target_node.id
                    refresh_list()
                    self.update_all_arrows()
                else:
                    _ = messagebox.showerror("Error", "Target not found.")
            except ValueError:
                _ = messagebox.showerror("Error", "Invalid integer.")

        def remove_transition():
            sel = listbox.curselection()
            if not sel:
                return
            text = listbox.get(sel[0])
            try:
                parts = text.split("->")
                ret_part = parts[0].strip()
                ret_val = int(ret_part.split()[1])
                if ret_val in node.connections:
                    del node.connections[ret_val]
                    refresh_list()
                    self.update_all_arrows()
            except (IndexError, ValueError):
                _ = messagebox.showerror("Error", "Could not parse transition.")

        btn_frame = tk.Frame(trans_win)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Transition",  command=add_transition)\
            .pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=remove_transition)\
            .pack(side=tk.LEFT, padx=5)
        tk.Button(trans_win, text="Close",           command=trans_win.destroy)\
            .pack(pady=5)

    def set_root(self):
        """Set the selected node as root."""
        if not self.selected_node:
            return
        for n in self.nodes:
            n.is_root = False
        self.selected_node.is_root = True
        self.draw_node(self.selected_node)
        self.select_node(self.selected_node)
        _ = messagebox.showinfo("Root Set", f"{self.selected_node.name} is now the root node.")

    def update_all_arrows(self):
        """Update all arrows of the mission graph."""
        self.canvas.delete("arrow")
        for node in self.nodes:
            for ret_val, target_id in node.connections.items():
                target = next((n for n in self.nodes if n.id == target_id), None)
                if target:
                    self.draw_arrow(node, target, ret_val)

    def draw_arrow(self, src: Node, tgt: Node, label) -> None:
        """Draw an arrow from src to tgt."""
        x1, y1 = src.x, src.y
        x2, y2 = tgt.x, tgt.y
        _ = self.canvas.create_line(x1, y1, x2, y2, fill="#aa0000",
                                    width=2, tags="arrow", arrow=tk.LAST)
        mx, my = (x1+x2)/2, (y1+y2)/2
        _ = self.canvas.create_text(mx, my-10, text=str(label), fill="blue",
                                    font=("Arial", 9), tags="arrow")

    def save_mission_to_disk(self):
        """Save the current mission to disk."""
        if not self.nodes:
            _ = messagebox.showwarning("Empty", "No nodes to save.")
            return

        mission_name = simpledialog.askstring("Save Mission", "Enter Mission Name (Folder name):")
        if not mission_name:
            return

        dir_path = os.path.join(os.getcwd(), mission_name)
        if os.path.exists(dir_path):
            if not messagebox.askyesno("Overwrite", f"Folder '{mission_name}' exists. Overwrite?"):
                return
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)

        for node in self.nodes:
            filename = f"node_{node.id}_{node.name}.py"
            filepath = os.path.join(dir_path, filename)
            with open(filepath, "w", encoding="UTF-8") as f:
                _ = f.write(node.code)

        meta = {
            "nodes": [],
            "next_id": self.next_id,
            "root_id": next((n.id for n in self.nodes if n.is_root), None)
        }
        for node in self.nodes:
            meta["nodes"].append({
                "id": node.id,
                "name": node.name,
                "x": node.x,
                "y": node.y,
                "code_file": f"node_{node.id}_{node.name}.py",
                "connections": node.connections
            })
        with open(os.path.join(dir_path, "mission.json"), "w", encoding="UTF-8") as f:
            json.dump(meta, f, indent=4)

        self.mission_folder = dir_path
        _ = messagebox.showinfo("Saved", f"Mission '{mission_name}' saved to:\n{dir_path}")

    def load_mission(self):
        """Load the mission from disk."""
        folder = filedialog.askdirectory(title="Select Mission Folder")
        if not folder:
            return
        meta_path = os.path.join(folder, "mission.json")
        if not os.path.exists(meta_path):
            _ = messagebox.showerror("Error", "mission.json not found.")
            return

        try:
            with open(meta_path, "r", encoding="UTF-8") as f:
                meta = json.load(f)
        except Exception:
            _ = messagebox.showerror("Error", "Invalid mission.json.")
            return

        self.new_mission()
        self.nodes = []
        self.canvas.delete("all")
        self.next_id = meta.get("next_id", 1)

        node_dict = {}
        for data in meta["nodes"]:
            node = Node(data["id"], data["name"], data["x"], data["y"])
            code_file = os.path.join(folder, data["code_file"])
            if os.path.exists(code_file):
                with open(code_file, "r", encoding="UTF-8") as cf:
                    node.code = cf.read()
            node.connections = data.get("connections", {})
            self.nodes.append(node)
            node_dict[node.id] = node
            self.draw_node(node)

        root_id = meta.get("root_id")
        if root_id and root_id in node_dict:
            node_dict[root_id].is_root = True
            self.draw_node(node_dict[root_id])

        self.mission_folder = folder
        self.update_all_arrows()
        _ = messagebox.showinfo("Loaded", f"Mission loaded from:\n{folder}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MissionEditorApp(root)
    root.mainloop()