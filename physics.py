r"""
Physics 1 - Project 9: Conservative Force & Energy Simulation Engine
Formulation:
    Force: F(x) = k*x - 4*q*x^3
    Potential Energy: U(x) = - \int F(x) dx = -0.5*k*x^2 + q*x^4  (assuming U(0) = 0)
    Kinetic Energy: K(t) = 0.5 * m * v(t)^2
    Total Energy: E(t) = K(t) + U(x(t))
    Equation of motion: m * d^2x/dt^2 = F(x) => dv/dt = (k/m)*x - (4*q/m)*x^3
"""

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from typing import Dict, Any, Tuple, List, Optional


class SymbolicConservativeForce:
    """
    Handles symbolic calculus using SymPy for the conservative force system:
        F(x) = k*x - 4*q*x^3
    """
    def __init__(self):
        self.x, self.k, self.q, self.m, self.t = sp.symbols('x k q m t', real=True)
        self.F_expr = self.k * self.x - 4 * self.q * self.x**3
        # U(x) = - \int F(x) dx
        self.U_expr = -sp.integrate(self.F_expr, self.x)  # -k*x**2 / 2 + q*x**4
        # d^2U/dx^2 = - dF/dx
        self.d2U_expr = sp.diff(self.U_expr, self.x, 2)

    def get_symbolic_formulas(self) -> Dict[str, str]:
        """Returns string and LaTeX representations of formulas."""
        return {
            "F_x_str": str(self.F_expr),
            "F_x_latex": sp.latex(self.F_expr),
            "U_x_str": str(self.U_expr),
            "U_x_latex": sp.latex(self.U_expr),
            "d2U_str": str(self.d2U_expr),
            "d2U_latex": sp.latex(self.d2U_expr),
            "ODE_str": f"d^2x/dt^2 = ({self.k}/m)*x - (4*{self.q}/m)*x^3",
            "ODE_latex": r"\frac{d^2x}{dt^2} = \frac{k}{m}x - \frac{4q}{m}x^3",
        }

    def find_equilibria(self, k_val: float, q_val: float) -> List[Dict[str, Any]]:
        """
        Finds equilibrium points where F(x) = 0, and determines stability
        via second derivative of potential energy U''(x).
        """
        results = []
        # F(x) = x * (k - 4*q*x^2) = 0
        # x = 0 always an equilibrium
        roots = [0.0]
        if q_val != 0:
            ratio = k_val / (4.0 * q_val)
            if ratio > 0:
                roots.append(np.sqrt(ratio))
                roots.append(-np.sqrt(ratio))

        roots = sorted(roots)
        for r in roots:
            # U''(x) = -k + 12*q*x^2
            d2U_val = -k_val + 12.0 * q_val * (r**2)
            if abs(d2U_val) < 1e-12:
                stability = "Neutral / Inflection"
            elif d2U_val > 0:
                stability = "Stable Minimum"
            else:
                stability = "Unstable Maximum"
            
            # Potential at this point:
            u_val = -0.5 * k_val * (r**2) + q_val * (r**4)
            results.append({
                "x": float(r),
                "U": float(u_val),
                "d2U": float(d2U_val),
                "stability": stability
            })
        return results

    def calculate_turning_points(self, k_val: float, q_val: float, E0: float) -> List[float]:
        """
        Finds roots of U(x) = E0 => q*x^4 - 0.5*k*x^2 - E0 = 0.
        Let u = x^2 >= 0:
        q*u^2 - 0.5*k*u - E0 = 0.
        """
        turning_points = []
        if abs(q_val) < 1e-14:
            # -0.5*k*x^2 = E0 => x^2 = -2*E0 / k
            if abs(k_val) > 1e-14:
                val = -2.0 * E0 / k_val
                if val >= 0:
                    turning_points.extend([np.sqrt(val), -np.sqrt(val)])
        else:
            # Quadratic in u: A = q, B = -0.5*k, C = -E0
            A = q_val
            B = -0.5 * k_val
            C = -E0
            disc = B**2 - 4 * A * C
            if disc >= 0:
                u1 = (-B + np.sqrt(disc)) / (2 * A)
                u2 = (-B - np.sqrt(disc)) / (2 * A)
                for u in [u1, u2]:
                    if u >= -1e-14:
                        u_clamped = max(0.0, u)
                        turning_points.append(np.sqrt(u_clamped))
                        turning_points.append(-np.sqrt(u_clamped))

        # Unique and sorted
        turning_points = sorted(list(set([round(float(tp), 6) for tp in turning_points])))
        return turning_points


class SimulationEngine:
    """
    Numerical integration engine using High-Precision Runge-Kutta (RK45/DOP853)
    and Symplectic Velocity Verlet integration.
    """
    def __init__(
        self,
        k: float = 4.0,
        q: float = 1.0,
        m: float = 1.0,
        x0: float = 0.5,
        v0: float = 0.0,
        t_span: Tuple[float, float] = (0.0, 20.0),
        n_points: int = 2000,
        method: str = "RK45"
    ):
        self.k = float(k)
        self.q = float(q)
        self.m = float(m)
        self.x0 = float(x0)
        self.v0 = float(v0)
        self.t_span = t_span
        self.n_points = int(n_points)
        self.method = method
        self.symbolic = SymbolicConservativeForce()

    def force(self, x: np.ndarray) -> np.ndarray:
        """Conservative force F(x) = k*x - 4*q*x^3"""
        return self.k * x - 4.0 * self.q * (x**3)

    def potential_energy(self, x: np.ndarray) -> np.ndarray:
        """Potential energy U(x) = -0.5*k*x^2 + q*x^4"""
        return -0.5 * self.k * (x**2) + self.q * (x**4)

    def kinetic_energy(self, v: np.ndarray) -> np.ndarray:
        """Kinetic energy K = 0.5 * m * v^2"""
        return 0.5 * self.m * (v**2)

    def _ode_rhs(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        ODEs:
        dx/dt = v
        dv/dt = F(x) / m = (k/m)*x - (4*q/m)*x^3
        """
        x, v = y[0], y[1]
        dxdt = v
        dvdt = (self.k * x - 4.0 * self.q * (x**3)) / self.m
        return np.array([dxdt, dvdt])

    def solve(self) -> Dict[str, Any]:
        """
        Executes numerical integration over the specified time span.
        Computes trajectories and verifies mechanical energy conservation.
        """
        if self.m <= 0:
            raise ValueError("Mass m must be positive.")
        if self.t_span[1] <= self.t_span[0]:
            raise ValueError("End time must be strictly greater than start time.")

        t_eval = np.linspace(self.t_span[0], self.t_span[1], self.n_points)
        y0 = [self.x0, self.v0]

        # Integrate ODE with tight tolerances to ensure minimal numerical drift
        sol = solve_ivp(
            fun=self._ode_rhs,
            t_span=self.t_span,
            y0=y0,
            t_eval=t_eval,
            method=self.method,
            rtol=1e-10,
            atol=1e-12
        )

        if not sol.success:
            raise RuntimeError(f"ODE integration failed: {sol.message}")

        t = sol.t
        x = sol.y[0]
        v = sol.y[1]
        a = (self.k * x - 4.0 * self.q * (x**3)) / self.m

        # Energy calculations
        K = self.kinetic_energy(v)
        U = self.potential_energy(x)
        E_total = K + U
        E0 = E_total[0]

        # Energy conservation metrics
        delta_E = np.abs(E_total - E0)
        max_delta_E = float(np.max(delta_E))
        mean_delta_E = float(np.mean(delta_E))
        rel_energy_error = float(max_delta_E / (abs(E0) + 1e-14))

        # Equilibrium points & turning points
        equilibria = self.symbolic.find_equilibria(self.k, self.q)
        turning_points = self.symbolic.calculate_turning_points(self.k, self.q, E0)

        # Estimate period if periodic
        period = self._estimate_period(t, x)

        return {
            "t": t,
            "x": x,
            "v": v,
            "a": a,
            "K": K,
            "U": U,
            "E_total": E_total,
            "E0": float(E0),
            "max_delta_E": max_delta_E,
            "mean_delta_E": mean_delta_E,
            "rel_energy_error": rel_energy_error,
            "equilibria": equilibria,
            "turning_points": turning_points,
            "period": period,
            "k": self.k,
            "q": self.q,
            "m": self.m,
            "x0": self.x0,
            "v0": self.v0,
            "t_span": self.t_span
        }

    def _estimate_period(self, t: np.ndarray, x: np.ndarray) -> Optional[float]:
        """Estimates oscillation period using peak detection."""
        # Find local peaks where slope changes from positive to negative
        dx = np.diff(x)
        peaks = np.where((dx[:-1] > 0) & (dx[1:] < 0))[0] + 1
        if len(peaks) >= 2:
            peak_times = t[peaks]
            periods = np.diff(peak_times)
            if len(periods) > 0:
                # Check consistency
                std_p = np.std(periods)
                mean_p = np.mean(periods)
                if std_p / (mean_p + 1e-9) < 0.1:  # Well-defined periodic motion
                    return float(mean_p)
        return None

    def get_potential_landscape(self, x_min: Optional[float] = None, x_max: Optional[float] = None, points: int = 500) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generates potential curve U(x) and Force F(x) over a suitable spatial range.
        """
        if x_min is None or x_max is None:
            # Automatic heuristic based on equilibria and initial position
            eq_x = [abs(eq["x"]) for eq in self.symbolic.find_equilibria(self.k, self.q)]
            scale = max([abs(self.x0), 1.0] + eq_x) * 1.5
            x_min = -scale
            x_max = scale

        x_grid = np.linspace(x_min, x_max, points)
        u_grid = self.potential_energy(x_grid)
        f_grid = self.force(x_grid)
        return x_grid, u_grid, f_grid
