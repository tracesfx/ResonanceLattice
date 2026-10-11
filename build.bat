@echo off
rem One-command build for Resonance Lattice: compile src\ -> jars\ResonanceLattice.jar -> validate.
cd /d "%~dp0"
python tools\build_mod.py %*
exit /b %errorlevel%
