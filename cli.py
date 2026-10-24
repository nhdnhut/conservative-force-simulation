"""
Physics 1 - Project 9: CLI / Standalone Runner
Kinetic and Potential Energy of a Particle under Conservative Force:
    F(x) = k*x - 4*q*x^3
    U(x) = -0.5*k*x^2 + q*x^4
"""

import argparse
import os
import sys

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import matplotlib.pyplot as plt
from physics import SimulationEngine, SymbolicConservativeForce


def run_cli():
    parser = argparse.ArgumentParser(
        description="Applied Physics 1 - Project 9: Conservative Force & Energy Simulation (CLI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-k", type=float, default=4.0, help="Linear force coefficient [N/m]")
    parser.add_argument("-q", type=float, default=1.0, help="Quartic force coefficient [N/m^3]")
    parser.add_argument("-m", type=float, default=1.0, help="Particle mass [kg]")
    parser.add_argument("--x0", type=float, default=0.6, help="Initial position x0 [m]")
    parser.add_argument("--v0", type=float, default=0.0, help="Initial velocity v0 [m/s]")
    parser.add_argument("--tmax", type=float, default=15.0, help="End time for simulation [s]")
    parser.add_argument("--points", type=int, default=2000, help="Number of sampling time points")
    parser.add_argument("--save-plots", action="store_true", help="Save high-res plots to current directory")
    parser.add_argument("--save-csv", action="store_true", help="Save trajectory data to CSV")
    parser.add_argument("--no-show", action="store_true", help="Do not display interactive matplotlib window")

    args = parser.parse_args()

    print("=" * 70)
    print("  APPLIED PHYSICS 1 - PROJECT 9: CONSERVATIVE FORCE & ENERGY")
    print("=" * 70)
    print(f"Parameters: k = {args.k} N/m, q = {args.q} N/m^3, m = {args.m} kg")
    print(f"Initial State: x0 = {args.x0} m, v0 = {args.v0} m/s")
    print(f"Time Horizon: [0.0, {args.tmax}] s with {args.points} points")
    print("-" * 70)

    # Symbolic derivations
    sym = SymbolicConservativeForce()
    formulas = sym.get_symbolic_formulas()
    print("[1] SYMBOLIC CALCULUS (SymPy):")
    print(f"    Force F(x)           : {formulas['F_x_str']}")
    print(f"    Potential U(x)       : {formulas['U_x_str']}  (Datum: U(0) = 0)")
    print(f"    Equation of Motion   : {formulas['ODE_str']}")

    # Equilibria
    eqs = sym.find_equilibria(args.k, args.q)
    print("\n[2] EQUILIBRIA & STABILITY:")
    for eq in eqs:
        print(f"    * x = {eq['x']:+.4f} m | U = {eq['U']:+.4f} J | d2U/dx2 = {eq['d2U']:+.4f} ({eq['stability']})")

    # Simulation
    print("\n[3] RUNNING NUMERICAL INTEGRATION (SciPy RK45)...")
    engine = SimulationEngine(
        k=args.k, q=args.q, m=args.m,
        x0=args.x0, v0=args.v0,
        t_span=(0.0, args.tmax),
        n_points=args.points
    )
    res = engine.solve()

    print("    Simulation completed successfully.")
    print("\n[4] ENERGY CONSERVATION METRICS:")
    print(f"    Initial Total Energy E0       : {res['E0']:.8f} J")
    print(f"    Max Absolute Drift max|dE|    : {res['max_delta_E']:.2e} J")
    print(f"    Relative Error (dE / E0)      : {res['rel_energy_error'] * 100:.6e} %")

    if res['turning_points']:
        tp_str = ", ".join([f"{tp:.4f}" for tp in res['turning_points']])
        print(f"    Classical Turning Points x_tp : [{tp_str}] m")
    else:
        print("    Classical Turning Points x_tp : None (Unbounded motion)")

    if res['period'] is not None:
        print(f"    Estimated Oscillation Period  : {res['period']:.4f} s (f = {1.0/res['period']:.3f} Hz)")
    else:
        print("    Estimated Oscillation Period  : Aperiodic / Barrier-crossing")

    # CSV Export
    if args.save_csv:
        csv_file = f"project9_sim_k{args.k}_q{args.q}_x0_{args.x0}.csv"
        data = np.column_stack([
            res["t"], res["x"], res["v"], res["a"], res["K"], res["U"], res["E_total"]
        ])
        header = "t_s,x_m,v_mps,a_mps2,K_J,U_J,E_total_J"
        np.savetxt(csv_file, data, delimiter=",", header=header, comments="# ")
        print(f"\n[+] Saved simulation CSV to: {csv_file}")

    # Generate multi-panel figure
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

    # Panel 1: Energy vs Time
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(res["t"], res["K"], label="Kinetic Energy K(t)", color="#dc2626", lw=2)
    ax1.plot(res["t"], res["U"], label="Potential Energy U(t)", color="#0284c7", lw=2)
    ax1.plot(res["t"], res["E_total"], label=f"Total Energy E(t) [E0={res['E0']:.3f}J]", color="#16a34a", lw=2.5, ls="--")
    ax1.set_title("Energy vs. Time (Conservation of Mechanical Energy)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Time t [s]")
    ax1.set_ylabel("Energy [J]")
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Panel 2: Kinematics (x(t) and v(t))
    ax2 = fig.add_subplot(gs[0, 1])
    ax2_v = ax2.twinx()
    l1 = ax2.plot(res["t"], res["x"], color="#2563eb", lw=2, label="Position x(t)")
    l2 = ax2_v.plot(res["t"], res["v"], color="#d97706", lw=1.8, ls="-.", label="Velocity v(t)")
    ax2.set_title("Kinematics: Position & Velocity vs. Time", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Time t [s]")
    ax2.set_ylabel("Position x [m]", color="#2563eb")
    ax2_v.set_ylabel("Velocity v [m/s]", color="#d97706")
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc="upper right", frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)

    # Panel 3: Potential Energy Landscape U(x)
    ax3 = fig.add_subplot(gs[1, 0])
    span = max(abs(float(np.min(res["x"]))), abs(float(np.max(res["x"]))), 1.2) * 1.3
    x_grid, u_grid, _ = engine.get_potential_landscape(-span, span, 400)
    ax3.plot(x_grid, u_grid, color="#0284c7", lw=2.2, label="U(x) = -1/2*kx^2 + qx^4")
    ax3.axhline(res["E0"], color="#16a34a", ls="--", lw=2, label=f"E0 = {res['E0']:.3f} J")
    ax3.fill_between(x_grid, u_grid, res["E0"], where=(u_grid > res["E0"]), color="#fee2e2", alpha=0.7, label="Forbidden (K < 0)")
    for eq in eqs:
        if -span <= eq["x"] <= span:
            marker = "o" if "Stable" in eq["stability"] else "^"
            c = "#16a34a" if "Stable" in eq["stability"] else "#dc2626"
            ax3.scatter([eq["x"]], [eq["U"]], color=c, marker=marker, s=70, zorder=5)
    for tp in res["turning_points"]:
        if -span <= tp <= span:
            ax3.scatter([tp], [res["E0"]], color="#d97706", marker="D", s=60, zorder=6)
    ax3.set_title("Potential Energy Landscape U(x) & Energy Level", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Position x [m]")
    ax3.set_ylabel("Energy [J]")
    ax3.legend(loc="upper right", frameon=True, fontsize=9)
    ax3.grid(True, linestyle=":", alpha=0.6)

    # Panel 4: Phase Space Orbit (v vs x)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(res["x"], res["v"], color="#7c3aed", lw=2, label="Phase Trajectory")
    ax4.scatter([res["x"][0]], [res["v"][0]], color="#16a34a", marker="o", s=80, label="Start Point", zorder=5)
    ax4.set_title("Phase Space Portrait (v vs. x)", fontsize=11, fontweight="bold")
    ax4.set_xlabel("Position x [m]")
    ax4.set_ylabel("Velocity v [m/s]")
    ax4.axhline(0, color="gray", ls=":", lw=1)
    ax4.axvline(0, color="gray", ls=":", lw=1)
    ax4.legend(loc="upper right", frameon=True)
    ax4.grid(True, linestyle=":", alpha=0.6)

    fig.suptitle(
        f"Applied Physics 1 — Project 9: Conservative Force F(x) = {args.k}x - 4({args.q})x³\n"
        f"Energy Conservation: ΔE/E₀ = {res['rel_energy_error']*100:.2e}%",
        fontsize=13, fontweight="bold"
    )

    if args.save_plots:
        img_name = "project9_summary_plot.png"
        fig.savefig(img_name, dpi=300, bbox_inches="tight")
        print(f"[+] Saved high-res figure to: {img_name}")

    if not args.no_show:
        plt.show()

    print("=" * 70)


if __name__ == "__main__":
    run_cli()
