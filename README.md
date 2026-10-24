# Conservative Force and Energy Simulation Suite

> A scientific simulation suite and interactive graphical application studying the kinetic and potential energy of a particle moving under an anharmonic conservative force.
> Numerical ODE Solver (Runge-Kutta RK45) | Symbolic Engine (SymPy) | CustomTkinter GUI | CLI Exporter | MATLAB Parity

[![Python](https://img.shields.io/badge/Python-3.10+-brightgreen?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-5%20Passed-brightgreen?style=flat-square)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## 1. Physical Model

The system studies the motion of a particle of mass $m$ subjected to an anharmonic conservative force:
$$F(x) = kx - 4qx^3$$

Integrating with respect to position gives the corresponding potential energy function:
$$U(x) = -\int F(x)dx = -\frac{1}{2}kx^2 + qx^4$$

The total mechanical energy remains conserved throughout the trajectory:
$$E = K(t) + U(t) = \frac{1}{2}m v(t)^2 - \frac{1}{2}k x(t)^2 + q x(t)^4 = \text{const}$$

---

## 2. Key Capabilities

1. Analytical and Symbolic Calculus:
   - SymPy-powered integration for symbolic potential functions and equilibrium root solving.
   - Second derivative curvature test for local minima (stable equilibria) and maxima (unstable equilibria).
   - Analytical turning point determination via energy intersection $U(x) = E_0$.
2. High-Precision Numerical Integration:
   - Adaptive Runge-Kutta (RK45) integration with strict error tolerances (relative tolerance $10^{-10}$).
   - Numerical verification of energy conservation with drift deltas $\Delta E / E_0 \lt 10^{-7}\%$.
3. Interactive Graphical User Interface:
   - Energy Analysis: Real-time curves for kinetic energy $K(t)$, potential energy $U(t)$, total energy $E(t)$, and numerical drift.
   - Phase Space Orbits: Parametric phase plane visualization $(x, v)$ illustrating bound periodic orbits.
   - Live Particle Dynamics: Dynamic canvas showing particle displacement along the potential curve with live energy bar distributions.
4. CLI Batch Exporter: Headless batch simulation runner supporting custom initial conditions, parameter sweeps, CSV telemetry dumps, and 300 DPI publication plots.
5. MATLAB Equivalent: Cross-verified `.m` script providing numerical parity for academic verification.

---

## 3. Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/nhdnhut/conservative-force-simulation.git
cd conservative-force-simulation

# Install dependencies
pip install numpy scipy sympy matplotlib customtkinter pytest
```

### Launch GUI Application
```bash
python main.py
```

### Run Headless CLI Simulation
```bash
python cli.py -k 4.0 -q 1.0 -m 1.0 --x0 0.6 --v0 0.0 --tmax 15.0 --save-plots --save-csv
```

### Run MATLAB Simulation
```matlab
run('project9_conservative_force.m')
```

### Run Automated Tests
```bash
pytest tests/ -v
```

---

## 4. Directory Structure

```
conservative-force-simulation/
├── main.py                          # Launcher entry point (auto-detects GUI/CLI)
├── gui.py                           # CustomTkinter graphical user interface
├── physics.py                       # Physics equations and numerical ODE solver
├── cli.py                           # Command-line interface and plot exporter
├── project9_conservative_force.m    # MATLAB implementation equivalent
├── REPORT.md                        # Academic lab report and mathematical derivations
├── tests/                           # Pytest unit tests
│   ├── conftest.py
│   └── test_physics.py
├── LICENSE                          # MIT License
└── README.md                        # Project documentation
```

---

## 5. Author and License

- Author: Nhut Nguyen (@nhdnhut)
- License: MIT License (see [LICENSE](LICENSE))

