"""Run the whole Athena pipeline in order (Sections E.3–E.9).

  python run_all.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [("E.3 extract and load", ["extract.py"]),
         ("E.4 resolve entities", ["resolve.py"]),
         ("E.5 reason and validate", ["reason.py"]),
         ("E.6 competency questions + GDS", ["questions.py"]),
         ("E.7 embed chunks", ["rag.py", "index"]),
         ("E.7 ask", ["rag.py"]),
         ("E.9 evaluate", ["evaluate.py"])]

for title, cmd in STEPS:
    print(f"\n===== {title} =====", flush=True)
    subprocess.run([sys.executable, *cmd], cwd=HERE, check=True)
print("\nDone. Serve it with:  uvicorn api:app --reload   (then open "
      "http://localhost:8000/)")
