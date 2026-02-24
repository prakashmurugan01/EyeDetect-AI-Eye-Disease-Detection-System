@echo off
REM ═══════════════════════════════════════════════════════════
REM  EyeDetect AI — Quick Setup Script (Windows)
REM ═══════════════════════════════════════════════════════════

echo.
echo  EyeDetect AI — Setup Script (Windows)
echo ========================================
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo Installing Python packages (this may take 5-10 minutes)...
pip install --upgrade pip
pip install -r requirements.txt

REM Copy .env
if not exist .env (
  copy .env.example .env
  echo Created .env - please edit it and add your OPENAI_API_KEY
)

REM Create media directories
mkdir media\uploads 2>nul
mkdir media\reports 2>nul
mkdir ml_models 2>nul
mkdir dataset\train\cataract 2>nul
mkdir dataset\train\diabetic_retinopathy 2>nul
mkdir dataset\train\glaucoma 2>nul
mkdir dataset\train\normal 2>nul
mkdir dataset\test\cataract 2>nul
mkdir dataset\test\diabetic_retinopathy 2>nul
mkdir dataset\test\glaucoma 2>nul
mkdir dataset\test\normal 2>nul

REM Run migrations
echo Running database migrations...
python manage.py makemigrations detection
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --no-input

echo.
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Edit .env and add your OPENAI_API_KEY
echo  2. Optional: Train model with: cd utils ^& python train_model.py
echo  3. Start server: python manage.py runserver
echo  4. Open: http://127.0.0.1:8000/
echo.
pause
