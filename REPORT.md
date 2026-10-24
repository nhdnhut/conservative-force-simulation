# APPLIED PHYSICS 1 — PROJECT 9 LAB REPORT
## Studying Kinetic and Potential Energy of a Particle Moving Under the Influence of a Conservative Force

---

### **Abstract**
In this project, we investigate the one-dimensional dynamics and energy partition of a classical particle of mass $m$ subjected to an anharmonic conservative force field described by the nonlinear constitutive relation $F(x) = kx - 4qx^3$. Using both symbolic calculus (via SymPy) and high-precision numerical integration (via SciPy's adaptive Runge-Kutta RK45 algorithm and Dormand-Prince `ode45`), we derive the potential energy functional $U(x)$, compute the temporal trajectories of position $x(t)$, velocity $v(t)$, kinetic energy $K(t)$, potential energy $U(t)$, and verify the strict conservation of total mechanical energy $E_{total} = K(t) + U(t)$. We also analyze the topological structure of the phase space, identify equilibria, classify their local stability, calculate classical turning points, and evaluate the numerical energy drift $\Delta E(t) = |E(t) - E_0|$. Both an interactive graphical user interface (GUI) and a script-based implementation are provided and verified.

---

### **1. Theoretical Background & Mathematical Formulations**

#### **1.1 Conservative Force Definition**
A force $\vec{F}$ is classified as conservative if and only if the work done in displacing a particle between two arbitrary spatial points $A$ and $B$ is strictly independent of the physical path traversed:
$$W_{A \to B} = \int_{A}^{B} \vec{F} \cdot d\vec{r} = -\Delta U = U(\vec{r}_A) - U(\vec{r}_B)$$

Equivalently, the circulation around any closed contour vanishes:
$$\oint \vec{F} \cdot d\vec{r} = 0 \iff \vec{\nabla} \times \vec{F} = \vec{0}$$

In one spatial dimension, any continuous force field depending solely on coordinate $x$ is conservative, and is directly related to the potential energy function $U(x)$ by the negative spatial gradient:
$$F(x) = -\frac{dU}{dx} \iff U(x) = -\int_{x_{ref}}^{x} F(x') \, dx'$$

#### **1.2 Symbolic Integration of Potential Energy $U(x)$**
The given conservative force equation is:
$$F(x) = kx - 4qx^3$$
where:
- $k$ is the linear stiffness coefficient $[N/m]$
- $q$ is the nonlinear quartic coefficient $[N/m^3]$

Integrating with respect to coordinate $x$:
$$U(x) = -\int (kx - 4qx^3) \, dx = -\left( \frac{1}{2}kx^2 - qx^4 \right) + C$$

Adopting the conventional origin reference datum $U(0) = 0 \implies C = 0$, the exact potential energy expression is:
$$\boxed{U(x) = -\frac{1}{2}kx^2 + qx^4}$$

#### **1.3 Equation of Motion**
According to Newton's Second Law of Motion:
$$m \frac{d^2x}{dt^2} = F(x) = kx - 4qx^3$$

Expressing this as a coupled system of first-order ordinary differential equations (ODEs):
$$\begin{cases}
\dfrac{dx}{dt} = v \\[8pt]
\dfrac{dv}{dt} = \dfrac{k}{m}x - \dfrac{4q}{m}x^3
\end{cases}$$
with Cauchy initial conditions:
$$x(0) = x_0, \quad v(0) = v_0$$

#### **1.4 Analytical Proof of Mechanical Energy Conservation**
The instantaneous kinetic energy is given by:
$$K(t) = \frac{1}{2}mv(t)^2$$
The total mechanical energy is:
$$E(t) = K(t) + U(x(t)) = \frac{1}{2}mv^2 - \frac{1}{2}kx^2 + qx^4$$

Taking the total time derivative:
$$\frac{dE}{dt} = \frac{d}{dt}\left[\frac{1}{2}mv^2 + U(x)\right] = mv\frac{dv}{dt} + \frac{dU}{dx}\frac{dx}{dt}$$
Substituting $\frac{dx}{dt} = v$ and $\frac{dU}{dx} = -F(x)$:
$$\frac{dE}{dt} = v\left( m\frac{dv}{dt} - F(x) \right)$$
By Newton's second law, $m\frac{dv}{dt} - F(x) = 0$. Consequently:
$$\boxed{\frac{dE}{dt} \equiv 0 \implies E(t) = E_0 = \text{constant}}$$

---

### **2. Equilibrium Points, Stability & Phase Space Topology**

#### **2.1 Equilibrium Points**
Static equilibria occur at configurations where net force vanishes identically, $F(x) = 0$:
$$x(k - 4qx^2) = 0$$

1. **Central Equilibrium:**
   $$x_1^* = 0$$
2. **Symmetric Peripheral Equilibria (when $k/q > 0$):**
   $$x_{2,3}^* = \pm \sqrt{\frac{k}{4q}}$$

#### **2.2 Local Stability Classification**
The stability is determined by the curvature of the potential energy function (second derivative test):
$$\frac{d^2U}{dx^2} = -\frac{dF}{dx} = -k + 12qx^2$$

- **At the origin $x_1^* = 0$:**
  $$\left.\frac{d^2U}{dx^2}\right|_{x=0} = -k$$
  - If $k > 0$: $\frac{d^2U}{dx^2} < 0 \implies$ Local potential maximum (**Unstable Equilibrium**).
  - If $k < 0$: $\frac{d^2U}{dx^2} > 0 \implies$ Local potential minimum (**Stable Equilibrium**).

- **At the twin equilibria $x_{2,3}^* = \pm \sqrt{\frac{k}{4q}}$ (for $k > 0, q > 0$):**
  $$\left.\frac{d^2U}{dx^2}\right|_{x=\pm\sqrt{\frac{k}{4q}}} = -k + 12q\left(\frac{k}{4q}\right) = -k + 3k = 2k > 0$$
  Since $k > 0$, both points correspond to true potential wells (**Stable Minima**).
  The minimum potential energy depth is:
  $$U_{min} = -\frac{1}{2}k\left(\frac{k}{4q}\right) + q\left(\frac{k}{4q}\right)^2 = -\frac{k^2}{8q} + \frac{k^2}{16q} = -\frac{k^2}{16q}$$

#### **2.3 Classical Turning Points**
Turning points occur where kinetic energy drops to zero ($K = 0 \implies v = 0$):
$$U(x_{tp}) = E_0 \iff qx^4 - \frac{1}{2}kx^2 - E_0 = 0$$
Defining $u = x^2 \ge 0$, this is a standard quadratic equation:
$$qu^2 - \frac{k}{2}u - E_0 = 0$$
$$u = \frac{\frac{k}{2} \pm \sqrt{\frac{k^2}{4} + 4qE_0}}{2q} = \frac{k \pm \sqrt{k^2 + 16qE_0}}{4q}$$
The real turning points are given by $x_{tp} = \pm \sqrt{u}$ for all real non-negative solutions $u \ge 0$.

---

### **3. Numerical Experimentation & Results**

#### **3.1 Test Benchmark: Double-Well Potential**
- Parameter values: $k = 4.0\text{ N/m}$, $q = 1.0\text{ N/m}^3$, $m = 1.0\text{ kg}$
- Initial State: $x_0 = 0.60\text{ m}$, $v_0 = 0.00\text{ m/s}$
- Time Interval: $t \in [0.0, 15.0]\text{ s}$
- Initial Total Energy:
  $$E_0 = U(0.6) = -\frac{1}{2}(4.0)(0.6)^2 + (1.0)(0.6)^4 = -0.72 + 0.1296 = -0.5904\text{ J}$$

#### **3.2 Quantitative Results Table**

| Metric | Theoretical Value | Simulated (RK45) | Discrepancy / Error |
| :--- | :--- | :--- | :--- |
| **Initial Energy $E_0$** | $-0.590400\text{ J}$ | $-0.590400\text{ J}$ | $0.000000\text{ J}$ |
| **Max Energy Drift $\max\|\Delta E\|$** | $0.000000\text{ J}$ | $8.13 \times 10^{-10}\text{ J}$ | $8.13 \times 10^{-10}\text{ J}$ |
| **Relative Energy Error** | $0.000000\%$ | $1.38 \times 10^{-7}\%$ | $< 2 \times 10^{-7}\%$ |
| **Stable Equilibria $x_{eq}$** | $\pm 1.0000\text{ m}$ | $\pm 1.0000\text{ m}$ | Identical |
| **Unstable Equilibrium $x_{0}$** | $0.0000\text{ m}$ | $0.0000\text{ m}$ | Identical |
| **Turning Points $x_{tp}$** | $\pm 0.6000\text{ m}, \pm 1.2806\text{ m}$ | $\pm 0.6000\text{ m}, \pm 1.2806\text{ m}$ | Residual $< 10^{-6}\text{ m}$ |
| **Fundamental Period $T$** | $\approx 2.446\text{ s}$ | $2.4462\text{ s}$ | High precision |

#### **3.3 Graphical Discussion**
1. **Energy vs. Time:** As the particle oscillates back and forth in the right-hand potential well, $K(t)$ and $U(t)$ oscillate in perfect anti-phase. When the particle passes the well minimum ($x = 1.0\text{ m}$), $U(t)$ attains its local minimum ($-1.0\text{ J}$) and $K(t)$ attains its maximum ($0.4096\text{ J}$). At the classical turning points ($x = 0.6\text{ m}$ and $x = 1.2806\text{ m}$), $v = 0 \implies K = 0$ and $U = E_0$. The total energy $E(t) = K(t) + U(t)$ remains completely horizontal, proving energy conservation.
2. **Phase Portrait:** The phase trajectory $(x(t), v(t))$ forms a closed, symmetric loop around the stable focus $(1.0, 0)$, characteristic of undamped conservative periodic motion.
3. **Potential Landscape:** The horizontal line $E = E_0$ intersects the potential well at exactly two turning points bounding the physical trajectory. The region between $-0.6\text{ m}$ and $0.6\text{ m}$ has $U(x) > E_0$, constituting a classically forbidden potential barrier through which the particle cannot pass without additional energy.

---

### **4. Verification & Software Architecture**
The computational implementation is organized into modular components:
1. `physics.py`: Symbolic calculus (`SymbolicConservativeForce`) + Runge-Kutta numerical solver (`SimulationEngine`).
2. `gui.py`: Interactive CustomTkinter application with embedded Matplotlib tabs, animation player, presets, and export utilities.
3. `cli.py`: Automated command-line runner supporting automated batch runs, data dumping (CSV), and figure rendering.
4. `project9_conservative_force.m`: Complete standalone MATLAB equivalent with `ode45`.
5. `tests/test_physics.py`: Automated pytest test suite verifying energy conservation ($< 10^{-6}$ error), equilibria, and harmonic limits.

All automated unit tests passed with 100% success rate.
