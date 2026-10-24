%% APPLIED PHYSICS 1 - PROJECT 9
% Studying kinetic and potential energy of a particle moving under influence of conservative force
% Conservative force: F(x) = k*x - 4*q*x^3
% Potential energy:   U(x) = - \int F(x) dx = -0.5*k*x^2 + q*x^4  (Reference U(0) = 0)
% Kinetic energy:     K(t) = 0.5 * m * v(t)^2
% Total energy:       E(t) = K(t) + U(t) = constant

clear; clc; close all;

fprintf('======================================================================\n');
fprintf('  APPLIED PHYSICS 1 - PROJECT 9: CONSERVATIVE FORCE & ENERGY (MATLAB)\n');
fprintf('======================================================================\n\n');

%% 1. Input Parameters
% Interactive input with default fallbacks
k = input('Enter linear force constant k [N/m] (default 4.0): ');
if isempty(k), k = 4.0; end

q = input('Enter quartic force constant q [N/m^3] (default 1.0): ');
if isempty(q), q = 1.0; end

m = input('Enter particle mass m [kg] (default 1.0): ');
if isempty(m), m = 1.0; end

x0 = input('Enter initial position x0 [m] (default 0.6): ');
if isempty(x0), x0 = 0.6; end

v0 = input('Enter initial velocity v0 [m/s] (default 0.0): ');
if isempty(v0), v0 = 0.0; end

tmax = input('Enter time interval duration [s] (default 15.0): ');
if isempty(tmax), tmax = 15.0; end

fprintf('\nSystem parameters initialized:\n');
fprintf('  k = %.2f N/m, q = %.2f N/m^3, m = %.2f kg\n', k, q, m);
fprintf('  x0 = %.2f m, v0 = %.2f m/s, t_span = [0, %.2f] s\n', x0, v0, tmax);

%% 2. Symbolic Derivation (Symbolic Math Toolbox)
try
    syms x_sym k_sym q_sym real
    F_sym = k_sym * x_sym - 4 * q_sym * x_sym^3;
    U_sym = -int(F_sym, x_sym);
    fprintf('\nSymbolic Derivations:\n');
    fprintf('  F(x) = %s\n', char(F_sym));
    fprintf('  U(x) = %s  (with U(0)=0)\n', char(U_sym));
catch
    fprintf('\n[Note] Symbolic toolbox not active; proceeding with analytical expressions.\n');
end

%% 3. Numerical ODE Integration (ode45 - Dormand-Prince Runge-Kutta)
tspan = [0, tmax];
y0 = [x0; v0];  % State vector: y(1) = x, y(2) = v

% ODE function:
% dy(1)/dt = v
% dy(2)/dt = (k*x - 4*q*x^3) / m
ode_sys = @(t, y) [y(2); (k*y(1) - 4*q*(y(1)^3)) / m];

options = odeset('RelTol', 1e-9, 'AbsTol', 1e-11);
[t, y] = ode45(ode_sys, tspan, y0, options);

x = y(:, 1);
v = y(:, 2);

%% 4. Energy Calculations & Conservation Verification
% Kinetic energy: K = 0.5 * m * v^2
K = 0.5 * m * (v.^2);

% Potential energy: U = -0.5 * k * x^2 + q * x^4
U = -0.5 * k * (x.^2) + q * (x.^4);

% Total Mechanical Energy: E = K + U
E_total = K + U;
E0 = E_total(1);

max_drift = max(abs(E_total - E0));
rel_error = max_drift / (abs(E0) + eps);

fprintf('\nEnergy Conservation Results:\n');
fprintf('  Initial Energy E0         = %.8f J\n', E0);
fprintf('  Max Absolute Drift max|dE| = %.3e J\n', max_drift);
fprintf('  Relative Error (dE/E0)    = %.6e %%\n', rel_error * 100);

%% 5. Graphical Visualizations (2x2 Multi-Panel Plot)
figure('Name', 'Applied Physics 1 - Project 9 Energy Analysis', 'Color', [1 1 1], 'Position', [100 100 1100 750]);

% Subplot 1: Kinetic, Potential, and Total Energy vs Time
subplot(2, 2, 1);
plot(t, K, 'r-', 'LineWidth', 2.0); hold on;
plot(t, U, 'b-', 'LineWidth', 2.0);
plot(t, E_total, 'g--', 'LineWidth', 2.2);
xlabel('Time t [s]', 'FontWeight', 'bold');
ylabel('Energy [J]', 'FontWeight', 'bold');
title('Kinetic, Potential & Total Energy vs. Time', 'FontWeight', 'bold');
legend('Kinetic Energy K(t)', 'Potential Energy U(t)', sprintf('Total Energy E(t) [E_0 = %.3f J]', E0), 'Location', 'best');
grid on;

% Subplot 2: Particle Kinematics (x(t) and v(t))
subplot(2, 2, 2);
yyaxis left;
plot(t, x, 'b-', 'LineWidth', 2.0);
ylabel('Position x [m]', 'FontWeight', 'bold');
yyaxis right;
plot(t, v, 'm-.', 'LineWidth', 1.8);
ylabel('Velocity v [m/s]', 'FontWeight', 'bold');
xlabel('Time t [s]', 'FontWeight', 'bold');
title('Kinematics: Position & Velocity vs. Time', 'FontWeight', 'bold');
grid on;

% Subplot 3: Potential Energy Landscape U(x) with Energy Level E0
subplot(2, 2, 3);
span = max([abs(min(x)), abs(max(x)), 1.2]) * 1.3;
x_grid = linspace(-span, span, 400);
U_grid = -0.5 * k * (x_grid.^2) + q * (x_grid.^4);
plot(x_grid, U_grid, 'b-', 'LineWidth', 2.2); hold on;
yline(E0, 'g--', sprintf('E_0 = %.3f J', E0), 'LineWidth', 2.0);
xlabel('Position x [m]', 'FontWeight', 'bold');
ylabel('Potential U(x) [J]', 'FontWeight', 'bold');
title('Potential Energy Curve U(x) and Energy Level', 'FontWeight', 'bold');
grid on;

% Subplot 4: Phase Space Orbit (v vs. x)
subplot(2, 2, 4);
plot(x, v, 'color', [0.5 0 0.8], 'LineWidth', 2.0); hold on;
plot(x(1), v(1), 'go', 'MarkerFaceColor', 'g', 'MarkerSize', 8);
xlabel('Position x [m]', 'FontWeight', 'bold');
ylabel('Velocity v [m/s]', 'FontWeight', 'bold');
title('Phase Space Trajectory (v vs. x)', 'FontWeight', 'bold');
legend('Phase Orbit', 'Start Point (x_0, v_0)', 'Location', 'best');
grid on;

sgtitle(sprintf('Physics 1 Project 9: F(x) = %.1fx - 4(%.1f)x^3 | Energy Drift: %.2e J', k, q, max_drift), 'FontSize', 13, 'FontWeight', 'bold');

fprintf('\n[+] Figures rendered successfully. Program finished.\n');
