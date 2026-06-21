"""
visualization/gui.py
Interactive GUI using Tkinter.
Now takes explicit input for Number of Obstacles and Deliveries.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from environment.grid import DeliveryGrid
from environment.scenarios import SCENARIOS
from agents.goal_agent import GoalBasedAgent


class DeliveryGUI:
    """Main GUI class using pure Tkinter Canvas."""

    COLORS = {
        0: "#FFFFFF",  # Road
        1: "#262626",  # Obstacle
        2: "#9933CC",  # Delivery
        3: "#FF9900",  # Traffic
    }
    START_COLOR = "#00CC00"
    PATH_COLOR = "#3380FF"
    CURRENT_COLOR = "#FFFF00"

    ALGO_LIST = ["BFS", "DFS", "UCS", "A*", "Hill Climbing"]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Delivery Route Optimizer — BS CS AI Lab")
        self.root.geometry("1150x780")
        self.root.configure(bg="#1a1a2e")

        self.grid_env = None
        self.animating = False
        self.anim_id = None
        self.cell_size = 25

        self._setup_styles()
        self._build_control_panel()
        self._build_grid_canvas()
        self._build_info_panel()
        self._generate_grid()

    # ------------------------------------------------------------------ #
    #                           STYLING                                   #
    # ------------------------------------------------------------------ #

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#1a1a2e")
        style.configure("Dark.TLabel", background="#1a1a2e", foreground="white", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#1a1a2e", foreground="#e94560", font=("Segoe UI", 14, "bold"))
        style.configure("Dark.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Run.TButton", font=("Segoe UI", 11, "bold"), padding=8, foreground="white", background="#e94560")
        style.configure("Dark.TLabelframe", background="#1a1a2e", foreground="white")
        style.configure("Dark.TLabelframe.Label", background="#1a1a2e", foreground="#e94560")
        style.configure("Dark.TEntry", fieldbackground="#0f3460", foreground="white")

    # ------------------------------------------------------------------ #
    #                      CONTROL PANEL (LEFT)                           #
    # ------------------------------------------------------------------ #

    def _build_control_panel(self) -> None:
        ctrl = ttk.Frame(self.root, style="Dark.TFrame", width=290)
        ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        ctrl.pack_propagate(False)

        ttk.Label(ctrl, text="DELIVERY OPTIMIZER", style="Title.TLabel").pack(pady=(5, 15))

        # ---- Scenario Selection ----
        sf = ttk.LabelFrame(ctrl, text=" Load Scenario ", style="Dark.TLabelframe")
        sf.pack(fill=tk.X, padx=5, pady=4)
        self.scenario_var = tk.StringVar(value="Scenario 1: Easy (10x10)")
        ttk.Combobox(sf, textvariable=self.scenario_var, values=list(SCENARIOS.keys()), state="readonly", width=30).pack(padx=8, pady=6)
        ttk.Button(sf, text="Load Scenario", style="Dark.TButton", command=self._load_scenario).pack(padx=8, pady=(0, 6))

        # ---- Algorithm Selection ----
        af = ttk.LabelFrame(ctrl, text=" Algorithm ", style="Dark.TLabelframe")
        af.pack(fill=tk.X, padx=5, pady=4)
        self.algo_var = tk.StringVar(value="A*")
        ttk.Combobox(af, textvariable=self.algo_var, values=self.ALGO_LIST, state="readonly", width=30).pack(padx=8, pady=6)

        # ---- Parameters & Inputs ----
        pf = ttk.LabelFrame(ctrl, text=" Parameters ", style="Dark.TLabelframe")
        pf.pack(fill=tk.X, padx=5, pady=4)
        
        # Sliders
        self.grid_size_var = tk.IntVar(value=10)
        self.hw_var = tk.IntVar(value=100)
        self.md_var = tk.IntVar(value=100)
        self.mi_var = tk.IntVar(value=500)

        self._make_slider(pf, "Grid Size", self.grid_size_var, 10, 25)
        
        # ✅ NEW: User Inputs for Obstacles and Deliveries
        self.obs_entry_var = tk.IntVar(value=10)
        self.deliv_entry_var = tk.IntVar(value=2)
        self._make_entry(pf, "Obstacles Count", self.obs_entry_var)
        self._make_entry(pf, "Deliveries Count", self.deliv_entry_var)

        self._make_slider(pf, "Heuristic Wt (A*)", self.hw_var, 50, 300)
        self._make_slider(pf, "Max Depth (DFS)", self.md_var, 10, 200)
        self._make_slider(pf, "Max Iters (Hill Climb)", self.mi_var, 100, 2000)

        # ---- Action Buttons ----
        bf = ttk.Frame(ctrl, style="Dark.TFrame")
        bf.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(bf, text="▶  GENERATE & RUN", style="Run.TButton", command=self._generate_and_run).pack(fill=tk.X, pady=3)
        ttk.Button(bf, text="▶  RUN ALL (Compare)", style="Run.TButton", command=self._run_all).pack(fill=tk.X, pady=3)
        ttk.Button(bf, text="⟳  RESET", style="Dark.TButton", command=self._reset).pack(fill=tk.X, pady=3)

    def _make_slider(self, parent, label: str, var: tk.IntVar, from_: int, to_: int) -> None:
        """Create a labeled slider."""
        frame = ttk.Frame(parent, style="Dark.TFrame")
        frame.pack(fill=tk.X, padx=8, pady=2)
        
        is_float = label == "Heuristic Wt (A*)"
        init_text = f"{label}: {var.get() / 100.0:.2f}" if is_float else f"{label}: {var.get()}"
        val_label = ttk.Label(frame, text=init_text, style="Dark.TLabel")
        val_label.pack(anchor=tk.W)

        def on_change(val):
            v = int(float(val))
            val_label.config(text=f"{label}: {v / 100.0:.2f}" if is_float else f"{label}: {v}")

        ttk.Scale(frame, from_=from_, to=to_, variable=var, orient=tk.HORIZONTAL, command=on_change).pack(fill=tk.X)

    def _make_entry(self, parent, label: str, var: tk.IntVar) -> None:
        """Create a labeled text input box."""
        frame = ttk.Frame(parent, style="Dark.TFrame")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(frame, text=f"{label}:", style="Dark.TLabel").pack(side=tk.LEFT)
        
        entry = tk.Entry(frame, textvariable=var, width=6, bg="#0f3460", fg="white", 
                         font=("Segoe UI", 11, "bold"), insertbackground="white", relief=tk.FLAT)
        entry.pack(side=tk.RIGHT, padx=5)

    # ------------------------------------------------------------------ #
    #                      GRID CANVAS (CENTER)                           #
    # ------------------------------------------------------------------ #

    def _build_grid_canvas(self) -> None:
        center = ttk.Frame(self.root, style="Dark.TFrame")
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=8)
        self.canvas = tk.Canvas(center, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------ #
    #                      INFO PANEL (RIGHT)                             #
    # ------------------------------------------------------------------ #

    def _build_info_panel(self) -> None:
        right = ttk.Frame(self.root, style="Dark.TFrame", width=300)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)
        right.pack_propagate(False)
        
        ttk.Label(right, text="RESULTS", style="Title.TLabel").pack(pady=(5, 8))
        self.info_text = tk.Text(right, height=20, width=34, bg="#0f3460", fg="#00ff00", 
                                 font=("Consolas", 10), relief=tk.FLAT, padx=10, pady=10, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=4)

    # ------------------------------------------------------------------ #
    #                     GRID GENERATION & DRAWING                       #
    # ------------------------------------------------------------------ #

    def _get_grid_inputs(self) -> tuple:
        """Read and validate user inputs. Returns (size, num_deliv, num_obs) or None if invalid."""
        try:
            size = self.grid_size_var.get()
            num_deliv = self.deliv_entry_var.get()
            num_obs = self.obs_entry_var.get()
            
            total_cells = size * size
            max_possible = total_cells - num_deliv - 5 # Leave space for start and traffic

            if num_deliv < 1:
                messagebox.showwarning("Input Error", "Deliveries must be at least 1!")
                return None
            if num_obs > max_possible:
                messagebox.showwarning("Input Error", f"Too many obstacles!\nMax allowed for {size}x{size} grid is {max_possible}.")
                return None
                
            return size, num_deliv, num_obs
            
        except tk.TclError:
            messagebox.showwarning("Input Error", "Please enter valid integer numbers!")
            return None

    def _generate_grid(self) -> None:
        """Generate grid silently (used for reset/scenario loading)."""
        self._stop_animation()
        size = self.grid_size_var.get()
        num_deliv = self.deliv_entry_var.get()
        num_obs = self.obs_entry_var.get()
        obs = num_obs / (size * size) if (size * size) > 0 else 0.0
        
        self.grid_env = DeliveryGrid(size=size, obstacle_density=obs, traffic_density=0.05, num_deliveries=num_deliv)
        self._draw_grid()

    def _generate_and_run(self) -> None:
        """Validate inputs, Generate grid, and Run selected algorithm."""
        inputs = self._get_grid_inputs()
        if not inputs: return
        
        size, num_deliv, num_obs = inputs
        self._stop_animation()
        
        # Calculate density for grid class
        obs = num_obs / (size * size)
        self.grid_env = DeliveryGrid(size=size, obstacle_density=obs, traffic_density=0.05, num_deliveries=num_deliv)
        self._draw_grid()
        
        # Now run the algorithm
        algo = self.algo_var.get()
        params = {
            "heuristic_weight": self.hw_var.get() / 100.0,
            "max_depth": self.md_var.get(),
            "max_iterations": self.mi_var.get()
        }
        
        agent = GoalBasedAgent(self.grid_env, algorithm=algo, **params)
        res = agent.plan_and_execute()
        
        info = (
            f"  Grid: {size}x{size} | Obs: {num_obs}\n"
            f"  Algorithm: {algo}\n"
            f"  ─────────────────────────\n"
            f"  Total Cost:    {res['total_cost']}\n"
            f"  Exec Time:     {res['time_ms']:.2f} ms\n"
            f"  Nodes Explored:{res['nodes_explored']}\n"
            f"  Deliveries:    {res['deliveries_visited']}/{res['total_deliveries']}\n"
            f"  ─────────────────────────\n"
        )
        for i, leg in enumerate(res["legs"]):
            status = "OK" if leg["success"] else "FAIL"
            info += f"  Leg {i+1}: Cost={leg['cost']}, Nodes={leg['nodes']} [{status}]\n"

        self._set_info(info)
        
        if res["path"]: 
            self._animate_path(res["path"])
        else: 
            messagebox.showinfo("Result", "No path found! Try reducing obstacles.")

    def _load_scenario(self) -> None:
        """Load pre-defined scenario and update input boxes."""
        self._stop_animation()
        sc = SCENARIOS[self.scenario_var.get()]
        size = sc["size"]
        
        # Update all UI elements to match scenario
        self.grid_size_var.set(size)
        self.deliv_entry_var.set(sc["num_deliveries"])
        
        # Calculate exact obstacles for this scenario
        exact_obs = int(size * size * sc["obstacle_density"])
        self.obs_entry_var.set(exact_obs)
        
        self.grid_env = DeliveryGrid(
            size=size, obstacle_density=sc["obstacle_density"], 
            traffic_density=sc["traffic_density"], 
            num_deliveries=sc["num_deliveries"], seed=sc["seed"]
        )
        self._draw_grid()
        self._set_info(f"  Loaded: {sc['description']}\n  Obstacles Set To: {exact_obs}\n  Deliveries Set To: {sc['num_deliveries']}\n\n  Click 'GENERATE & RUN' to execute.")

    def _draw_grid(self, path: list = None, step: int = -1) -> None:
        """Render the grid and path on Tkinter canvas."""
        self.canvas.delete("all")
        if not self.grid_env: return
        
        g = self.grid_env
        size = g.rows
        
        canvas_w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 500
        canvas_h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 500
        self.cell_size = max(5, min(canvas_w, canvas_h) // size)

        offset_x = (canvas_w - size * self.cell_size) // 2
        offset_y = (canvas_h - size * self.cell_size) // 2

        path_set = set(path[:step+1]) if path else set()

        for r in range(size):
            for c in range(size):
                x1 = offset_x + c * self.cell_size
                y1 = offset_y + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = self.COLORS.get(g.grid[r][c], "#FFFFFF")
                if (r, c) in path_set: color = self.PATH_COLOR
                if (r, c) == g.start: color = self.START_COLOR
                    
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333333", width=1)

        if path and 0 <= step < len(path):
            cr, cc = path[step]
            cx = offset_x + cc * self.cell_size + self.cell_size // 2
            cy = offset_y + cr * self.cell_size + self.cell_size // 2
            rad = max(3, self.cell_size // 3)
            self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad, fill=self.CURRENT_COLOR, outline="")

    # ------------------------------------------------------------------ #
    #                          ANIMATION                                  #
    # ------------------------------------------------------------------ #

    def _animate_path(self, path: list) -> None:
        self.animating = True
        delay = max(5, 1000 // max(len(path), 1))
        def _step(i):
            if not self.animating or i >= len(path):
                self.animating = False
                self._draw_grid(path, len(path)-1)
                return
            self._draw_grid(path, i)
            self.anim_id = self.root.after(delay, _step, i+1)
        _step(0)

    def _stop_animation(self) -> None:
        self.animating = False
        if self.anim_id: self.root.after_cancel(self.anim_id)
        self.anim_id = None

    # ------------------------------------------------------------------ #
    #                        RUN ACTIONS                                  #
    # ------------------------------------------------------------------ #

    def _run_all(self) -> None:
        """Run all 5 algorithms on current grid."""
        inputs = self._get_grid_inputs()
        if not inputs: return
        
        size, num_deliv, num_obs = inputs
        self._stop_animation()
        
        obs = num_obs / (size * size)
        self.grid_env = DeliveryGrid(size=size, obstacle_density=obs, traffic_density=0.05, num_deliveries=num_deliv)
        self._draw_grid()

        params = {
            "heuristic_weight": self.hw_var.get() / 100.0,
            "max_depth": self.md_var.get(),
            "max_iterations": self.mi_var.get()
        }
        
        info = "   ALGORITHM COMPARISON\n"
        info += "  ═══════════════════════════\n"
        info += f"  Grid: {size}x{size} | Obs: {num_obs} | Del: {num_deliv}\n"
        info += f"  {'Algo':<14} {'Cost':>5} {'Time':>9} {'Nodes':>7}\n"
        info += "  ─────────────────────────────\n"
        
        best_path = []
        for algo in self.ALGO_LIST:
            res = GoalBasedAgent(self.grid_env, algorithm=algo, **params).plan_and_execute()
            info += f"  {algo:<14} {res['total_cost']:>5} {res['time_ms']:>7.1f}ms {res['nodes_explored']:>7}\n"
            if algo == "A*" and res["path"]: best_path = res["path"]
            
        self._set_info(info)
        if best_path: self._draw_grid(best_path)
        messagebox.showinfo("Comparison Complete", "All 5 algorithms executed!")

    def _reset(self) -> None:
        """Reset all inputs to defaults."""
        self._stop_animation()
        self.algo_var.set("A*")
        self.grid_size_var.set(10)
        self.obs_entry_var.set(10)
        self.deliv_entry_var.set(2)
        self.hw_var.set(100)
        self.md_var.set(100)
        self.mi_var.set(500)
        self._set_info("  Reset Done!\n  Set Obstacles & Deliveries,\n  then click GENERATE & RUN.")
        self._generate_grid()

    # ------------------------------------------------------------------ #
    #                        INFO HELPERS                                 #
    # ------------------------------------------------------------------ #

    def _set_info(self, text: str) -> None:
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)
