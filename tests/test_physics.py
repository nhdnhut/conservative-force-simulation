"""
Unit Tests for Physics 1 - Project 9 Simulation Engine
"""

import pytest
import numpy as np
import sympy as sp
from physics import SymbolicConservativeForce, SimulationEngine


def test_symbolic_force_and_potential():
    sym = SymbolicConservativeForce()
    formulas = sym.get_symbolic_formulas()
    
    # Check symbolic potential U(x) = -k*x^2/2 + q*x^4
    x, k, q = sp.symbols('x k q', real=True)
    expected_U = -k * x**2 / 2 + q * x**4
    assert sp.simplify(sym.U_expr - expected_U) == 0

    # Check dU/dx = -F(x)
    assert sp.simplify(sp.diff(sym.U_expr, sym.x) + sym.F_expr) == 0


def test_equilibria_double_well():
    sym = SymbolicConservativeForce()
    # k = 4.0, q = 1.0 => x = 0, x = +- sqrt(4/(4*1)) = +- 1.0
    eqs = sym.find_equilibria(k_val=4.0, q_val=1.0)
    assert len(eqs) == 3
    x_vals = [round(eq["x"], 4) for eq in eqs]
    assert x_vals == [-1.0, 0.0, 1.0]

    # Stability checks: x = +-1 is minimum, x = 0 is maximum
    for eq in eqs:
        if abs(eq["x"]) == 1.0:
            assert "Stable" in eq["stability"]
            assert eq["U"] == -1.0  # -0.5*4*(1)^2 + 1*(1)^4 = -2 + 1 = -1.0 J
        elif eq["x"] == 0.0:
            assert "Unstable" in eq["stability"]
            assert eq["U"] == 0.0


def test_energy_conservation_rk45():
    # Intra-well oscillation inside double well: k=4.0, q=1.0, m=1.0, x0=0.6, v0=0.0
    engine = SimulationEngine(k=4.0, q=1.0, m=1.0, x0=0.6, v0=0.0, t_span=(0.0, 20.0), n_points=2000)
    res = engine.solve()

    # Initial energy
    E0_expected = -0.5 * 4.0 * (0.6**2) + 1.0 * (0.6**4)  # -0.72 + 0.1296 = -0.5904 J
    assert pytest.approx(res["E0"], rel=1e-5) == E0_expected

    # Energy conservation drift must be negligible (< 1e-6 relative error)
    assert res["rel_energy_error"] < 1e-6
    assert res["max_delta_E"] < 1e-8


def test_harmonic_oscillator_limit():
    # In limit q=0, k < 0 (let k = -4.0, so F = -4x is standard spring F = -K_s * x)
    # m = 1.0 => omega = sqrt(4/1) = 2 rad/s => T = 2*pi / omega = pi approx 3.14159 s
    engine = SimulationEngine(k=-4.0, q=0.0, m=1.0, x0=1.0, v0=0.0, t_span=(0.0, 15.0), n_points=3000)
    res = engine.solve()

    assert res["period"] is not None
    assert pytest.approx(res["period"], rel=0.02) == np.pi
    assert res["rel_energy_error"] < 1e-7


def test_turning_points():
    sym = SymbolicConservativeForce()
    # E0 = -0.5904 with k=4, q=1
    E0 = -0.5904
    tps = sym.calculate_turning_points(k_val=4.0, q_val=1.0, E0=E0)
    # Check that U(tp) == E0
    for tp in tps:
        u_val = -0.5 * 4.0 * (tp**2) + 1.0 * (tp**4)
        assert pytest.approx(u_val, abs=1e-4) == E0
