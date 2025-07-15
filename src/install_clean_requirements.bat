@echo off
echo Installing only required external Python libraries...
IF EXIST clean_requirements.txt (
    pip install -r clean_requirements.txt
    echo ✅ Clean installation complete.
) ELSE (
    echo ❌ clean_requirements.txt not found.
)
pause
