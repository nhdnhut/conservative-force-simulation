@echo off
chcp 65001 >nul
title Applied Physics 1 - Project 9 Launcher
cls

echo ======================================================================
echo    APPLIED PHYSICS 1 - PROJECT 9: CONSERVATIVE FORCE SIMULATION
echo             F(x) = k*x - 4*q*x^3  ^|  U(x) = -1/2*k*x^2 + q*x^4
echo ======================================================================
echo.
echo  [1] Launch Modern GUI Application (CustomTkinter + Animation)
echo  [2] Run CLI Simulation ^& Generate 300 DPI Plots + CSV
echo  [3] Run Automated Unit Tests (pytest)
echo  [4] Run CLI with Custom Parameters
echo  [5] Exit
echo.
echo ======================================================================

choice /C 12345 /N /T 8 /D 1 /M "Select option [1-5] (Auto-launches GUI [1] in 8s): "

if errorlevel 5 goto exit_script
if errorlevel 4 goto launch_cli_custom
if errorlevel 3 goto run_tests
if errorlevel 2 goto launch_cli_default
if errorlevel 1 goto launch_gui

:launch_gui
echo.
echo [*] Launching Modern GUI Application...
python main.py
goto end

:launch_cli_default
echo.
echo [*] Running CLI Simulation with default parameters...
python cli.py -k 4.0 -q 1.0 -m 1.0 --x0 0.6 --v0 0.0 --tmax 15.0 --save-plots --save-csv
goto end

:run_tests
echo.
echo [*] Running Pytest Unit Tests...
python -m pytest -v
goto end

:launch_cli_custom
echo.
echo Enter simulation parameters (press Enter to keep default):
set /p k_val="Linear constant k [N/m] (default 4.0): "
set /p q_val="Quartic constant q [N/m^3] (default 1.0): "
set /p m_val="Mass m [kg] (default 1.0): "
set /p x0_val="Initial position x0 [m] (default 0.6): "
set /p v0_val="Initial velocity v0 [m/s] (default 0.0): "
set /p tmax_val="Time duration [s] (default 15.0): "

if "%k_val%"=="" set k_val=4.0
if "%q_val%"=="" set q_val=1.0
if "%m_val%"=="" set m_val=1.0
if "%x0_val%"=="" set x0_val=0.6
if "%v0_val%"=="" set v0_val=0.0
if "%tmax_val%"=="" set tmax_val=15.0

echo.
echo [*] Running simulation: k=%k_val%, q=%q_val%, m=%m_val%, x0=%x0_val%, v0=%v0_val%, tmax=%tmax_val%
python cli.py -k %k_val% -q %q_val% -m %m_val% --x0 %x0_val% --v0 %v0_val% --tmax %tmax_val% --save-plots --save-csv
goto end

:end
echo.
echo ======================================================================
echo Program finished. Press any key to exit...
pause >nul

:exit_script
exit /b 0
