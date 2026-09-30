from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SIMULATION = ROOT / "simulation"
VISUALISER = ROOT / "visualiser"
VENV = SIMULATION / ".venv"

if os.name == "nt":
    python_exe = VENV / "Scripts" / "python.exe"
    pip_exe = VENV / "Scripts" / "pip.exe"
else:
    python_exe = VENV / "bin" / "python"
    pip_exe = VENV / "bin" / "pip"

if not VENV.exists():
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])

subprocess.check_call([
    str(pip_exe),
    "install",
    "-r",
    str(SIMULATION / "requirements.txt")
])

if not (VISUALISER / "node_modules").exists():
    subprocess.check_call(["npm", "install"], cwd=VISUALISER, shell=os.name == "nt")

simulation = subprocess.Popen(
    [str(python_exe), "src/app.py"],
    cwd=SIMULATION
)

visualiser = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=VISUALISER,
    shell=os.name == "nt"
)

try:
    simulation.wait()
    visualiser.wait()
except KeyboardInterrupt:
    simulation.terminate()
    visualiser.terminate()