@echo off
cd /d "%~dp0"
echo Running Ridgeline tests. This window closes when done (about 3-5 minutes)...
(
echo === where ===
where python
where claude
python --version
echo === pip ===
python -m pip install -q -r requirements.txt
echo === tests ===
python run_tests.py
echo === done ===
) > run_log.txt 2>&1
