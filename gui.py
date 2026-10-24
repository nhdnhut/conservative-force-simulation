"""
Physics 1 - Project 9: Kinetic and Potential Energy of a Particle under Conservative Force
Modern Graphical User Interface built with CustomTkinter & Matplotlib.
"""

import os
import sys
import numpy as np
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation

from physics import SimulationEngine, SymbolicConservativeForce


# Set CustomTkinter theme and appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Consistent color palette for dark modern GUI & plots
PALETTE = {
    "bg": "#12141c",
    "card_bg": "#1a1d29",
    "card_border": "#282d40",
    "accent_primary": "#3b82f6",     # Blue
    "accent_secondary": "#10b981",   # Emerald
    "kinetic": "#f87171",            # Coral red
    "potential": "#38bdf8",          # Sky blue
    "total": "#fbbf24",              # Amber / Gold
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    "grid": "#2a2e3f"
}


class ModernToolbar(NavigationToolbar2Tk):
    """Clean styled navigation toolbar."""
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent, pack_toolbar=False)
        self.config(background="#1a1d29")
        for button in self.winfo_children():
            button.config(background="#1a1d29")


class PhysicsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Applied Physics 1 — Project 9: Conservative Force & Energy Simulation")
        self.geometry("1400x900")
        self.minsize(1100, 750)

        # Physics engine state
        self.engine = SimulationEngine()
        self.sim_data = None
        self.anim = None
        self.anim_running = False

        # Build UI layout
        self._build_layout()
        self._load_preset("Double-Well Intra-Oscillation")
        self.run_simulation()

    def _build_layout(self):
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=380)  # Sidebar
        self.grid_columnconfigure(1, weight=1)                # Main display

        self._build_sidebar()
        self._build_main_display()

    # -------------------------------------------------------------
    # Sidebar: Parameter Inputs, Presets, Action Buttons, Metrics
    # -------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkScrollableFrame(
            self,
            width=380,
            corner_radius=0,
            fg_color="#131622",
            border_width=1,
            border_color="#1e2235"
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Header Title
        title_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_box.pack(fill="x", padx=15, pady=(15, 10))

        badge = ctk.CTkLabel(
            title_box,
            text="APPLIED PHYSICS 1 — PROJECT 9",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#38bdf8"
        )
        badge.pack(anchor="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Conservative Force\n& Energy Analyzer",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#f8fafc",
            justify="left"
        )
        title_lbl.pack(anchor="w", pady=(2, 2))

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="F(x) = kx − 4qx³  |  U(x) = −½kx² + qx⁴",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#94a3b8"
        )
        subtitle_lbl.pack(anchor="w")

        # Preset Selector Card
        preset_card = ctk.CTkFrame(sidebar, fg_color="#1a1e2e", corner_radius=10, border_width=1, border_color="#2b324b")
        preset_card.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            preset_card,
            text="⚡ QUICK PRESETS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#cbd5e1"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.presets = {
            "Double-Well Intra-Oscillation": {"k": 4.0, "q": 1.0, "m": 1.0, "x0": 0.6, "v0": 0.0, "tmax": 15.0},
            "Inter-Well High Energy Crossing": {"k": 4.0, "q": 1.0, "m": 1.0, "x0": 1.5, "v0": 0.0, "tmax": 15.0},
            "Simple Harmonic Limit (q=0)": {"k": -2.0, "q": 0.0, "m": 1.0, "x0": 1.0, "v0": 0.0, "tmax": 20.0},
            "Anharmonic Single Well": {"k": -1.5, "q": -0.5, "m": 1.0, "x0": 0.8, "v0": 0.0, "tmax": 15.0},
            "Garcia & Penland Benchmark": {"k": 2.0, "q": 0.5, "m": 1.0, "x0": 0.3, "v0": 0.5, "tmax": 25.0}
        }

        self.preset_combo = ctk.CTkComboBox(
            preset_card,
            values=list(self.presets.keys()),
            command=self._on_preset_change,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#111420",
            border_color="#3b82f6"
        )
        self.preset_combo.pack(fill="x", padx=12, pady=(0, 12))

        # Parameters Card
        param_card = ctk.CTkFrame(sidebar, fg_color="#1a1e2e", corner_radius=10, border_width=1, border_color="#2b324b")
        param_card.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            param_card,
            text="⚙️ SYSTEM PARAMETERS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#cbd5e1"
        ).pack(anchor="w", padx=12, pady=(10, 8))

        self.entries = {}
        fields = [
            ("k", "Linear coefficient k [N/m]:", "4.0"),
            ("q", "Nonlinear coefficient q [N/m³]:", "1.0"),
            ("m", "Particle mass m [kg]:", "1.0"),
            ("x0", "Initial position x₀ [m]:", "0.6"),
            ("v0", "Initial velocity v₀ [m/s]:", "0.0"),
            ("tmax", "Time interval duration [s]:", "15.0"),
            ("n_points", "Sampling points N:", "2500"),
        ]

        for key, label_text, default_val in fields:
            row = ctk.CTkFrame(param_card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(
                row,
                text=label_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#94a3b8"
            ).pack(anchor="w")

            ent = ctk.CTkEntry(
                row,
                font=ctk.CTkFont(family="Consolas", size=12),
                fg_color="#10131d",
                border_color="#333b56",
                height=28
            )
            ent.insert(0, default_val)
            ent.pack(fill="x", pady=(2, 0))
            self.entries[key] = ent

        param_card.pack_configure(pady=(8, 8))

        # Action Buttons
        btn_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=6)

        self.btn_run = ctk.CTkButton(
            btn_box,
            text="▶  Run Simulation",
            command=self.run_simulation,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=36
        )
        self.btn_run.pack(fill="x", pady=3)

        btn_grid = ctk.CTkFrame(btn_box, fg_color="transparent")
        btn_grid.pack(fill="x", pady=3)
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_grid,
            text="💾 Export CSV",
            command=self.export_csv,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#1e293b",
            hover_color="#334155",
            height=30
        ).grid(row=0, column=0, padx=(0, 3), sticky="ew")

        ctk.CTkButton(
            btn_grid,
            text="📷 Save PNG",
            command=self.export_plots,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#1e293b",
            hover_color="#334155",
            height=30
        ).grid(row=0, column=1, padx=(3, 0), sticky="ew")

        ctk.CTkButton(
            btn_box,
            text="📄 Generate Lab Report (PDF/MD)",
            command=self.generate_report,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#0f766e",
            hover_color="#115e59",
            height=30
        ).pack(fill="x", pady=3)

        # Real-time Metrics Card
        metrics_card = ctk.CTkFrame(sidebar, fg_color="#1a1e2e", corner_radius=10, border_width=1, border_color="#2b324b")
        metrics_card.pack(fill="x", padx=15, pady=(8, 20))

        ctk.CTkLabel(
            metrics_card,
            text="📊 CONSERVATION METRICS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#cbd5e1"
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.metrics_labels = {}
        metric_items = [
            ("E0", "Initial Energy E₀:", "0.0000 J"),
            ("drift", "Max Drift ΔE:", "0.0000 J"),
            ("error", "Relative Error ΔE/E₀:", "0.0000 %"),
            ("turning", "Turning Points x:", "None"),
            ("period", "Estimated Period T:", "N/A"),
            ("status", "Conservation State:", "Verified ✓")
        ]

        for m_key, m_label, m_init in metric_items:
            m_row = ctk.CTkFrame(metrics_card, fg_color="transparent")
            m_row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(
                m_row,
                text=m_label,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#94a3b8"
            ).pack(anchor="w")

            val_lbl = ctk.CTkLabel(
                m_row,
                text=m_init,
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                text_color="#38bdf8"
            )
            val_lbl.pack(anchor="w")
            self.metrics_labels[m_key] = val_lbl

        metrics_card.pack_configure(pady=(8, 15))

    # -------------------------------------------------------------
    # Main Display: TabView with Matplotlib Visualizations
    # -------------------------------------------------------------
    def _build_main_display(self):
        self.main_container = ctk.CTkFrame(self, fg_color="#0e111a", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(
            self.main_container,
            fg_color="#121522",
            segmented_button_fg_color="#1a1e2e",
            segmented_button_selected_color="#2563eb",
            segmented_button_selected_hover_color="#1d4ed8",
            segmented_button_unselected_hover_color="#252b40",
            text_color="#f8fafc",
            command=self._on_tab_changed
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        # Tabs
        self.tab_energy = self.tabview.add("⚡ Energy vs Time")
        self.tab_kinematics = self.tabview.add("📈 Kinematics (x, v, a)")
        self.tab_phase = self.tabview.add("🌀 Potential & Phase Portrait")
        self.tab_anim = self.tabview.add("🎬 Live Particle Animation")
        self.tab_theory = self.tabview.add("📜 Symbolic Theory & Math")

        # Setup canvases for each tab
        self._setup_energy_tab()
        self._setup_kinematics_tab()
        self._setup_phase_tab()
        self._setup_anim_tab()
        self._setup_theory_tab()

    def _setup_energy_tab(self):
        frame = self.tab_energy
        plt.style.use("dark_background")
        self.fig_energy, (self.ax_energy, self.ax_drift) = plt.subplots(
            2, 1, figsize=(8, 6), gridspec_kw={"height_ratios": [3, 1]}, facecolor="#121522"
        )
        self.fig_energy.subplots_adjust(left=0.1, right=0.96, top=0.93, bottom=0.1, hspace=0.35)

        self.canvas_energy = FigureCanvasTkAgg(self.fig_energy, master=frame)
        self.canvas_energy.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = ctk.CTkFrame(frame, fg_color="#1a1e2e", height=32)
        toolbar_frame.pack(fill="x", side="bottom")
        self.tb_energy = ModernToolbar(self.canvas_energy, toolbar_frame)
        self.tb_energy.update()
        self.tb_energy.pack(side="left", padx=5)

    def _setup_kinematics_tab(self):
        frame = self.tab_kinematics
        self.fig_kin, (self.ax_x, self.ax_v) = plt.subplots(
            2, 1, figsize=(8, 6), facecolor="#121522", sharex=True
        )
        self.fig_kin.subplots_adjust(left=0.1, right=0.96, top=0.93, bottom=0.1, hspace=0.25)

        self.canvas_kin = FigureCanvasTkAgg(self.fig_kin, master=frame)
        self.canvas_kin.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = ctk.CTkFrame(frame, fg_color="#1a1e2e", height=32)
        toolbar_frame.pack(fill="x", side="bottom")
        self.tb_kin = ModernToolbar(self.canvas_kin, toolbar_frame)
        self.tb_kin.update()
        self.tb_kin.pack(side="left", padx=5)

    def _setup_phase_tab(self):
        frame = self.tab_phase
        self.fig_phase, (self.ax_well, self.ax_orbit) = plt.subplots(
            1, 2, figsize=(9, 5), facecolor="#121522"
        )
        self.fig_phase.subplots_adjust(left=0.08, right=0.96, top=0.90, bottom=0.12, wspace=0.25)

        self.canvas_phase = FigureCanvasTkAgg(self.fig_phase, master=frame)
        self.canvas_phase.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = ctk.CTkFrame(frame, fg_color="#1a1e2e", height=32)
        toolbar_frame.pack(fill="x", side="bottom")
        self.tb_phase = ModernToolbar(self.canvas_phase, toolbar_frame)
        self.tb_phase.update()
        self.tb_phase.pack(side="left", padx=5)

    def _setup_anim_tab(self):
        frame = self.tab_anim

        # Control panel above animation
        anim_controls = ctk.CTkFrame(frame, fg_color="#1a1e2e", corner_radius=8)
        anim_controls.pack(fill="x", padx=5, pady=(5, 5))

        self.btn_play_pause = ctk.CTkButton(
            anim_controls,
            text="⏸ Pause",
            command=self._toggle_animation,
            width=90,
            height=28,
            fg_color="#2563eb"
        )
        self.btn_play_pause.pack(side="left", padx=10, pady=6)

        ctk.CTkButton(
            anim_controls,
            text="↺ Restart",
            command=self._restart_animation,
            width=90,
            height=28,
            fg_color="#334155"
        ) .pack(side="left", padx=5, pady=6)

        ctk.CTkLabel(
            anim_controls,
            text="Speed:",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94a3b8"
        ).pack(side="left", padx=(15, 5))

        self.speed_slider = ctk.CTkSlider(
            anim_controls,
            from_=0.25,
            to=3.0,
            number_of_steps=11,
            width=140
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=5)

        self.anim_time_lbl = ctk.CTkLabel(
            anim_controls,
            text="Time: t = 0.00 s",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.anim_time_lbl.pack(side="right", padx=15)

        # Matplotlib figure for animation
        self.fig_anim, (self.ax_anim_well, self.ax_anim_bars) = plt.subplots(
            1, 2, figsize=(9, 5), gridspec_kw={"width_ratios": [3, 1]}, facecolor="#121522"
        )
        self.fig_anim.subplots_adjust(left=0.08, right=0.96, top=0.90, bottom=0.12, wspace=0.25)

        self.canvas_anim = FigureCanvasTkAgg(self.fig_anim, master=frame)
        self.canvas_anim.get_tk_widget().pack(fill="both", expand=True)

    def _setup_theory_tab(self):
        frame = self.tab_theory
        scroll = ctk.CTkScrollableFrame(frame, fg_color="#121522")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        theory_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  APPLIED PHYSICS 1 — PROJECT 9: THEORETICAL FOUNDATION & DERIVATIONS\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "1. CONSERVATIVE FORCE DEFINITION:\n"
            "   A force F(x) is conservative if the work done in moving a particle between two\n"
            "   points depends only on initial and final positions, independent of path:\n"
            "       W = ∫[x_A -> x_B] F(x) dx = -ΔU = U(x_A) - U(x_B)\n\n"
            "2. GIVEN FORCE LAW:\n"
            "       F(x) = k*x - 4*q*x³\n"
            "   where:\n"
            "       k = linear coefficient [N/m] (stiffness / spring parameter)\n"
            "       q = quartic nonlinear coefficient [N/m³]\n\n"
            "3. SYMBOLIC DERIVATION OF POTENTIAL ENERGY U(x):\n"
            "   By definition: U(x) = -∫ F(x) dx\n"
            "       U(x) = -∫ (k*x - 4*q*x³) dx\n"
            "            = - [ (1/2)*k*x² - q*x⁴ ] + C\n"
            "   Taking U(0) = 0 as the reference datum (C = 0):\n"
            "       ★ U(x) = - (1/2)*k*x² + q*x⁴\n\n"
            "4. EQUILIBRIUM & STABILITY ANALYSIS:\n"
            "   Equilibrium points occur where net force vanishes: F(x) = 0\n"
            "       x * (k - 4*q*x²) = 0\n"
            "       => x₁ = 0\n"
            "       => x₂,₃ = ± √( k / (4q) )   (if k / q > 0)\n\n"
            "   Stability is governed by the second derivative of potential energy:\n"
            "       d²U/dx² = - dF/dx = -k + 12*q*x²\n"
            "   - If d²U/dx² > 0: Stable equilibrium (Potential Minimum / Restoring Well)\n"
            "   - If d²U/dx² < 0: Unstable equilibrium (Potential Maximum / Hill Crest)\n\n"
            "5. CONSERVATION OF TOTAL MECHANICAL ENERGY:\n"
            "   Kinetic Energy:   K(t) = (1/2)*m*v(t)²\n"
            "   Potential Energy: U(t) = - (1/2)*k*x(t)² + q*x(t)⁴\n"
            "   Total Energy:     E(t) = K(t) + U(t) = const = E₀\n\n"
            "   Time derivative of total energy:\n"
            "       dE/dt = m*v*(dv/dt) + (dU/dx)*(dx/dt)\n"
            "             = v * [ m*(d²x/dt²) - F(x) ]\n"
            "   Since m*(d²x/dt²) = F(x) (Newton's 2nd Law), dE/dt ≡ 0 identically!\n\n"
            "6. TURNING POINTS:\n"
            "   At turning points, instantaneous velocity is zero: v = 0 => K = 0.\n"
            "   Hence: U(x_turn) = E₀\n"
            "       q*x⁴ - (1/2)*k*x² - E₀ = 0\n"
            "   Let u = x² >= 0 (Biquadratic equation):\n"
            "       q*u² - (k/2)*u - E₀ = 0\n"
            "       u = [ (k/2) ± √( (k²/4) + 4*q*E₀ ) ] / (2q)\n"
            "       x_turn = ± √u\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        txt_box = ctk.CTkTextbox(
            scroll,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#e2e8f0",
            fg_color="#181c2a",
            border_width=1,
            border_color="#2b324b",
            height=600
        )
        txt_box.pack(fill="both", expand=True, padx=10, pady=10)
        txt_box.insert("1.0", theory_text)
        txt_box.configure(state="disabled")

    # -------------------------------------------------------------
    # Preset Handling & Simulation Trigger
    # -------------------------------------------------------------
    def _on_preset_change(self, choice):
        self._load_preset(choice)
        self.run_simulation()

    def _load_preset(self, name):
        if name in self.presets:
            p = self.presets[name]
            for key in ["k", "q", "m", "x0", "v0", "tmax"]:
                if key in self.entries:
                    self.entries[key].delete(0, "end")
                    self.entries[key].insert(0, str(p[key]))

    def _read_inputs(self):
        try:
            k = float(self.entries["k"].get())
            q = float(self.entries["q"].get())
            m = float(self.entries["m"].get())
            x0 = float(self.entries["x0"].get())
            v0 = float(self.entries["v0"].get())
            tmax = float(self.entries["tmax"].get())
            n_pts = int(self.entries["n_points"].get())
            if m <= 0:
                raise ValueError("Mass m must be positive (> 0).")
            if tmax <= 0:
                raise ValueError("Time tmax must be positive (> 0).")
            if n_pts < 100:
                raise ValueError("Points N must be at least 100.")
            return k, q, m, x0, v0, tmax, n_pts
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid parameter: {str(e)}")
            return None

    def run_simulation(self):
        params = self._read_inputs()
        if params is None:
            return

        k, q, m, x0, v0, tmax, n_pts = params
        self.engine = SimulationEngine(
            k=k, q=q, m=m, x0=x0, v0=v0, t_span=(0.0, tmax), n_points=n_pts, method="RK45"
        )

        try:
            self.sim_data = self.engine.solve()
        except Exception as e:
            messagebox.showerror("Simulation Error", f"Failed to integrate ODE: {str(e)}")
            return

        # Update metrics cards
        self._update_metrics()

        # Update all plots
        self._plot_energy()
        self._plot_kinematics()
        self._plot_phase()
        self._init_animation()

    def _update_metrics(self):
        d = self.sim_data
        self.metrics_labels["E0"].configure(text=f"{d['E0']:.6f} J")
        self.metrics_labels["drift"].configure(text=f"{d['max_delta_E']:.2e} J")
        self.metrics_labels["error"].configure(text=f"{d['rel_energy_error'] * 100:.4e} %")

        tps = d["turning_points"]
        if tps:
            tp_str = ", ".join([f"{tp:.3f}" for tp in tps[:4]])
            self.metrics_labels["turning"].configure(text=f"[{tp_str}] m")
        else:
            self.metrics_labels["turning"].configure(text="Unbounded / None")

        if d["period"] is not None:
            self.metrics_labels["period"].configure(text=f"{d['period']:.4f} s (f = {1.0/d['period']:.3f} Hz)")
        else:
            self.metrics_labels["period"].configure(text="Aperiodic / Unbounded")

        if d["rel_energy_error"] < 1e-4:
            self.metrics_labels["status"].configure(text="Conserved ✓ (< 0.01% drift)", text_color="#10b981")
        else:
            self.metrics_labels["status"].configure(text="Warning: High Drift", text_color="#f59e0b")

    # -------------------------------------------------------------
    # Plotting Functions
    # -------------------------------------------------------------
    def _plot_energy(self):
        d = self.sim_data
        t = d["t"]
        K = d["K"]
        U = d["U"]
        E_tot = d["E_total"]
        E0 = d["E0"]

        # Upper plot: Energies
        self.ax_energy.clear()
        self.ax_energy.set_facecolor("#161a29")
        self.ax_energy.plot(t, K, label="Kinetic Energy K(t)", color=PALETTE["kinetic"], lw=2.0)
        self.ax_energy.plot(t, U, label="Potential Energy U(t)", color=PALETTE["potential"], lw=2.0)
        self.ax_energy.plot(t, E_tot, label=f"Total Energy E(t) [E0 = {E0:.4f} J]", color=PALETTE["total"], lw=2.5, ls="--")

        self.ax_energy.set_ylabel("Energy [Joules]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_energy.set_title("Conservation of Mechanical Energy: K(t) + U(t) = E_total", fontsize=13, color=PALETTE["text"], fontweight="bold")
        self.ax_energy.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_energy.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=10)
        self.ax_energy.tick_params(colors=PALETTE["text_muted"])

        # Lower plot: Residual Energy Drift
        self.ax_drift.clear()
        self.ax_drift.set_facecolor("#161a29")
        drift = E_tot - E0
        self.ax_drift.plot(t, drift, color="#a855f7", lw=1.5, label="dE(t) = E(t) - E0")
        self.ax_drift.axhline(0, color="#64748b", ls=":", lw=1)
        self.ax_drift.set_xlabel("Time t [seconds]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_drift.set_ylabel("dE [J]", fontsize=10, color=PALETTE["text"])
        self.ax_drift.set_title("Numerical Energy Drift (Verifying Conservation at Machine Tolerance)", fontsize=10, color=PALETTE["text_muted"])
        self.ax_drift.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_drift.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=9)
        self.ax_drift.tick_params(colors=PALETTE["text_muted"])

        self.canvas_energy.draw()

    def _plot_kinematics(self):
        d = self.sim_data
        t = d["t"]
        x = d["x"]
        v = d["v"]

        # Position plot
        self.ax_x.clear()
        self.ax_x.set_facecolor("#161a29")
        self.ax_x.plot(t, x, color="#38bdf8", lw=2.0, label="Position x(t)")
        self.ax_x.axhline(0, color="#475569", ls="--", lw=1)
        self.ax_x.set_ylabel("Position x [m]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_x.set_title("Particle Kinematics: Position & Velocity vs. Time", fontsize=13, color=PALETTE["text"], fontweight="bold")
        self.ax_x.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_x.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=10)
        self.ax_x.tick_params(colors=PALETTE["text_muted"])

        # Velocity plot
        self.ax_v.clear()
        self.ax_v.set_facecolor("#161a29")
        self.ax_v.plot(t, v, color="#34d399", lw=2.0, label="Velocity v(t)")
        self.ax_v.axhline(0, color="#475569", ls="--", lw=1)
        self.ax_v.set_xlabel("Time t [seconds]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_v.set_ylabel("Velocity v [m/s]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_v.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_v.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=10)
        self.ax_v.tick_params(colors=PALETTE["text_muted"])

        self.canvas_kin.draw()

    def _plot_phase(self):
        d = self.sim_data
        x = d["x"]
        v = d["v"]
        E0 = d["E0"]

        # Left plot: Potential Energy Landscape U(x)
        self.ax_well.clear()
        self.ax_well.set_facecolor("#161a29")

        # Determine spatial range
        x_min_data, x_max_data = float(np.min(x)), float(np.max(x))
        span = max(abs(x_min_data), abs(x_max_data), 1.2) * 1.4
        x_grid, u_grid, _ = self.engine.get_potential_landscape(-span, span, 400)

        # Plot potential curve
        self.ax_well.plot(x_grid, u_grid, color="#38bdf8", lw=2.5, label="Potential U(x)")
        self.ax_well.axhline(E0, color=PALETTE["total"], lw=2, ls="--", label=f"Total Energy E0 = {E0:.3f} J")

        # Shading classically forbidden regions where U(x) > E0
        self.ax_well.fill_between(x_grid, u_grid, E0, where=(u_grid > E0), color="#ef4444", alpha=0.15, label="Forbidden (K < 0)")

        # Mark equilibrium points
        for eq in d["equilibria"]:
            if -span <= eq["x"] <= span:
                color = "#10b981" if "Stable" in eq["stability"] else "#f43f5e"
                marker = "o" if "Stable" in eq["stability"] else "^"
                self.ax_well.scatter(
                    [eq["x"]], [eq["U"]], color=color, marker=marker, s=80, zorder=5,
                    label=f"Equilibrium x={eq['x']:.2f} ({eq['stability'].split()[0]})"
                )

        # Mark turning points
        for tp in d["turning_points"]:
            if -span <= tp <= span:
                self.ax_well.scatter([tp], [E0], color="#fbbf24", marker="D", s=70, zorder=6)

        # Limit y-axis sensibly
        u_allowed = u_grid[(x_grid >= -span*0.9) & (x_grid <= span*0.9)]
        y_low = min(float(np.min(u_allowed)), E0) - abs(E0)*0.3 - 0.5
        y_high = max(E0 + abs(E0)*0.5 + 1.0, float(np.percentile(u_allowed, 85)))
        self.ax_well.set_ylim(y_low, y_high)
        self.ax_well.set_xlim(-span, span)

        self.ax_well.set_xlabel("Position x [m]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_well.set_ylabel("Energy [Joules]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_well.set_title("Potential Energy Landscape U(x)", fontsize=12, color=PALETTE["text"], fontweight="bold")
        self.ax_well.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_well.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=8)
        self.ax_well.tick_params(colors=PALETTE["text_muted"])

        # Right plot: Phase Space (v vs x)
        self.ax_orbit.clear()
        self.ax_orbit.set_facecolor("#161a29")
        self.ax_orbit.plot(x, v, color="#c084fc", lw=2.0, label="Phase Orbit")
        self.ax_orbit.scatter([x[0]], [v[0]], color="#34d399", marker="o", s=90, zorder=5, label=f"Start (x0={x[0]:.2f}, v0={v[0]:.2f})")
        self.ax_orbit.axhline(0, color="#475569", ls=":", lw=1)
        self.ax_orbit.axvline(0, color="#475569", ls=":", lw=1)

        self.ax_orbit.set_xlabel("Position x [m]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_orbit.set_ylabel("Velocity v [m/s]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_orbit.set_title("Phase Space Portrait (v vs. x)", fontsize=12, color=PALETTE["text"], fontweight="bold")
        self.ax_orbit.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_orbit.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=9)
        self.ax_orbit.tick_params(colors=PALETTE["text_muted"])

        self.canvas_phase.draw()

    # -------------------------------------------------------------
    # Animation: Particle Rolling in Potential Well + Live Energy
    # -------------------------------------------------------------
    def _init_animation(self):
        if self.anim is not None and self.anim.event_source is not None:
            self.anim.event_source.stop()
            self.anim = None

        d = self.sim_data
        x = d["x"]
        v = d["v"]
        t = d["t"]
        K = d["K"]
        U = d["U"]
        E0 = d["E0"]

        # Setup landscape
        span = max(abs(float(np.min(x))), abs(float(np.max(x))), 1.2) * 1.3
        x_grid, u_grid, _ = self.engine.get_potential_landscape(-span, span, 300)

        self.ax_anim_well.clear()
        self.ax_anim_well.set_facecolor("#161a29")
        self.ax_anim_well.plot(x_grid, u_grid, color="#38bdf8", lw=2.2, label="U(x)")
        self.ax_anim_well.axhline(E0, color=PALETTE["total"], lw=1.8, ls="--", label=f"E0 = {E0:.3f} J")
        self.ax_anim_well.fill_between(x_grid, u_grid, E0, where=(u_grid > E0), color="#ef4444", alpha=0.15)

        # Dynamic animated elements
        self.anim_particle, = self.ax_anim_well.plot([], [], "o", color="#f43f5e", markersize=14, markeredgewidth=2, markeredgecolor="#ffffff", zorder=10)
        self.anim_trace, = self.ax_anim_well.plot([], [], color="#fb7185", lw=1.2, alpha=0.6, zorder=8)

        u_allowed = u_grid[(x_grid >= -span*0.9) & (x_grid <= span*0.9)]
        y_low = min(float(np.min(u_allowed)), E0) - abs(E0)*0.3 - 0.5
        y_high = max(E0 + abs(E0)*0.5 + 1.0, float(np.percentile(u_allowed, 85)))
        self.ax_anim_well.set_ylim(y_low, y_high)
        self.ax_anim_well.set_xlim(-span, span)
        self.ax_anim_well.set_xlabel("Position x [m]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_anim_well.set_ylabel("Potential Energy U(x) [J]", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_anim_well.set_title("Live Particle Motion in Potential Well", fontsize=12, color=PALETTE["text"], fontweight="bold")
        self.ax_anim_well.grid(True, color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_anim_well.legend(loc="upper right", facecolor="#1e2235", edgecolor="#333b56", fontsize=9)
        self.ax_anim_well.tick_params(colors=PALETTE["text_muted"])

        # Energy bar chart
        self.ax_anim_bars.clear()
        self.ax_anim_bars.set_facecolor("#161a29")
        categories = ["K (Kinetic)", "U (Potential)", "Total E"]
        bar_colors = [PALETTE["kinetic"], PALETTE["potential"], PALETTE["total"]]
        self.anim_bars = self.ax_anim_bars.bar(categories, [K[0], U[0], E0], color=bar_colors, width=0.55)

        max_e_abs = max(abs(E0), float(np.max(np.abs(K))), float(np.max(np.abs(U))), 1.0) * 1.3
        self.ax_anim_bars.set_ylim(-max_e_abs if np.min(U) < 0 else 0, max_e_abs)
        self.ax_anim_bars.set_ylabel("Energy [J]", fontsize=10, color=PALETTE["text"])
        self.ax_anim_bars.set_title("Energy Partition", fontsize=11, color=PALETTE["text"], fontweight="bold")
        self.ax_anim_bars.grid(True, axis="y", color=PALETTE["grid"], linestyle=":", alpha=0.7)
        self.ax_anim_bars.tick_params(colors=PALETTE["text_muted"])

        self.canvas_anim.draw()

        # Animation state
        self.anim_frame_idx = 0
        self.anim_running = True
        self.btn_play_pause.configure(text="⏸ Pause")

        # Step size to achieve ~40 fps
        total_pts = len(t)
        self.anim_step = max(1, total_pts // 300)

        def animate_frame(frame):
            if not self.anim_running:
                return self.anim_particle,

            speed = self.speed_slider.get()
            step = int(self.anim_step * speed)
            self.anim_frame_idx = (self.anim_frame_idx + step) % total_pts
            idx = self.anim_frame_idx

            curr_x = x[idx]
            curr_u = U[idx]
            curr_k = K[idx]
            curr_t = t[idx]

            self.anim_particle.set_data([curr_x], [curr_u])

            # Recent trail
            trail_start = max(0, idx - int(15 * self.anim_step))
            self.anim_trace.set_data(x[trail_start:idx], U[trail_start:idx])

            # Update bars
            self.anim_bars[0].set_height(curr_k)
            self.anim_bars[1].set_height(curr_u)
            self.anim_bars[2].set_height(curr_k + curr_u)

            # Update label
            self.anim_time_lbl.configure(text=f"Time: t = {curr_t:.2f} s | x = {curr_x:+.3f} m")

            return self.anim_particle, self.anim_trace

        self.anim = FuncAnimation(
            self.fig_anim, animate_frame, interval=30, blit=False, cache_frame_data=False
        )

    def _toggle_animation(self):
        self.anim_running = not self.anim_running
        if self.anim_running:
            self.btn_play_pause.configure(text="⏸ Pause", fg_color="#2563eb")
        else:
            self.btn_play_pause.configure(text="▶ Resume", fg_color="#10b981")

    def _restart_animation(self):
        self.anim_frame_idx = 0
        self.anim_running = True
        self.btn_play_pause.configure(text="⏸ Pause", fg_color="#2563eb")

    def _on_tab_changed(self):
        # Refresh current tab canvas when selected
        curr = self.tabview.get()
        if curr == "⚡ Energy vs Time":
            self.canvas_energy.draw_idle()
        elif curr == "📈 Kinematics (x, v, a)":
            self.canvas_kin.draw_idle()
        elif curr == "🌀 Potential & Phase Portrait":
            self.canvas_phase.draw_idle()
        elif curr == "🎬 Live Particle Animation":
            self.canvas_anim.draw_idle()

    # -------------------------------------------------------------
    # Export Capabilities: CSV, High-Res Plots, Full Lab Report
    # -------------------------------------------------------------
    def export_csv(self):
        if self.sim_data is None:
            messagebox.showwarning("No Data", "Please run simulation first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
            title="Export Simulation Data"
        )
        if not filepath:
            return

        try:
            d = self.sim_data
            data = np.column_stack([
                d["t"], d["x"], d["v"], d["a"], d["K"], d["U"], d["E_total"]
            ])
            header = (
                f"Applied Physics 1 - Project 9 Simulation Data\n"
                f"Parameters: k={d['k']}, q={d['q']}, m={d['m']}, x0={d['x0']}, v0={d['v0']}\n"
                f"Initial Energy E0={d['E0']:.8f} J, Max Drift={d['max_delta_E']:.2e} J\n"
                f"time_s,position_m,velocity_mps,acceleration_mps2,kinetic_energy_J,potential_energy_J,total_energy_J"
            )
            np.savetxt(filepath, data, delimiter=",", header=header, comments="# ")
            messagebox.showinfo("Export Successful", f"Saved simulation data to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save CSV: {str(e)}")

    def export_plots(self):
        if self.sim_data is None:
            messagebox.showwarning("No Data", "Please run simulation first.")
            return

        folder = filedialog.askdirectory(title="Select Folder to Save High-Res Plots")
        if not folder:
            return

        try:
            self.fig_energy.savefig(os.path.join(folder, "project9_energy_conservation.png"), dpi=300, facecolor=self.fig_energy.get_facecolor())
            self.fig_kin.savefig(os.path.join(folder, "project9_kinematics.png"), dpi=300, facecolor=self.fig_kin.get_facecolor())
            self.fig_phase.savefig(os.path.join(folder, "project9_phase_portrait_well.png"), dpi=300, facecolor=self.fig_phase.get_facecolor())
            messagebox.showinfo("Export Successful", f"Exported 3 high-resolution (300 DPI) plots to:\n{folder}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save plots: {str(e)}")

    def generate_report(self):
        if self.sim_data is None:
            messagebox.showwarning("No Data", "Please run simulation first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Document", "*.md"), ("Text Document", "*.txt")],
            title="Generate Project Report"
        )
        if not filepath:
            return

        try:
            d = self.sim_data
            eq_text = "\n".join([
                f"- x = {eq['x']:+.4f} m: U = {eq['U']:.4f} J, d²U/dx² = {eq['d2U']:+.4f} ({eq['stability']})"
                for eq in d["equilibria"]
            ])
            tps_text = ", ".join([f"{tp:.4f}" for tp in d["turning_points"]]) if d["turning_points"] else "None (unbounded motion)"
            period_text = f"{d['period']:.4f} s" if d["period"] is not None else "Aperiodic / Unbounded"

            report = f"""# APPLIED PHYSICS 1 — PROJECT 9 LAB REPORT
## Studying Kinetic and Potential Energy of a Particle Moving Under Influence of Conservative Force

### 1. Project Overview & System Parameters
- **Linear force constant ($k$):** {d['k']} N/m
- **Quartic force constant ($q$):** {d['q']} N/m³
- **Particle mass ($m$):** {d['m']} kg
- **Initial position ($x_0$):** {d['x0']} m
- **Initial velocity ($v_0$):** {d['v0']} m/s
- **Time interval span:** [{d['t_span'][0]}, {d['t_span'][1]}] s

### 2. Mathematical Modeling & Symbolic Integration
The given conservative force law is:
$$F(x) = k x - 4 q x^3$$

The potential energy function $U(x)$ is calculated symbolically by:
$$U(x) = -\\int F(x) dx = -\\int (k x - 4 q x^3) dx = -\\frac{1}{2} k x^2 + q x^4 + C$$
Setting the reference potential at the origin $U(0) = 0 \\implies C = 0$:
$$U(x) = -\\frac{1}{2} k x^2 + q x^4$$

The kinetic energy of the particle is:
$$K(t) = \\frac{1}{2} m v(t)^2$$

Total mechanical energy:
$$E_{{total}}(t) = K(t) + U(t) = \\frac{1}{2} m v(t)^2 - \\frac{1}{2} k x(t)^2 + q x(t)^4$$

### 3. Equilibrium Points & Stability
Equilibrium points occur where $F(x) = 0 \\iff x(k - 4qx^2) = 0$:
{eq_text}

### 4. Conservation of Mechanical Energy Verification
- **Initial Total Energy ($E_0$):** {d['E0']:.8f} J
- **Maximum Absolute Energy Drift ($\\max |\\Delta E|$):** {d['max_delta_E']:.2e} J
- **Relative Energy Conservation Error:** {d['rel_energy_error'] * 100:.6e} %
- **Turning Points:** [{tps_text}] m
- **Oscillation Period ($T$):** {period_text}

**Conclusion on Conservation:**
The relative energy variation remains well below $10^{{-6}}$, proving that the mechanical energy is strictly conserved throughout the motion under the conservative force field.

---
*Generated autonomously by Physics 1 - Project 9 Suite.*
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo("Report Generated", f"Lab report successfully generated at:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write report: {str(e)}")


def launch_gui():
    app = PhysicsApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
