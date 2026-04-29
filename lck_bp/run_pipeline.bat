@echo off
cd C:\Users\user\lck-bp-project\lck_bp
call C:\Users\user\lck-bp-project\venv\Scripts\activate
python fetch_lck_data.py >> logs\pipeline.log 2>&1
if %errorlevel% neq 0 (
    echo %date% %time% FAILED >> logs\pipeline_status.log
) else (
    echo %date% %time% SUCCESS >> logs\pipeline_status.log
)