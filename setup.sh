#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  EyeDetect AI — Quick Setup Script (Linux / macOS)
# ═══════════════════════════════════════════════════════════

set -e

echo ""
echo "👁️  EyeDetect AI — Setup Script"
echo "================================"
echo ""

# 1. Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
echo "⬇️  Installing Python packages (this may take 5-10 minutes)..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 3. Copy .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✏️  Created .env — please edit it and add your OPENAI_API_KEY"
fi

# 4. Create media directories
mkdir -p media/uploads media/reports media/uploads/webcam
mkdir -p ml_models
mkdir -p dataset/train/{cataract,diabetic_retinopathy,glaucoma,normal}
mkdir -p dataset/test/{cataract,diabetic_retinopathy,glaucoma,normal}

# 5. Run migrations
echo "🗃️  Running database migrations..."
python manage.py makemigrations detection --no-input
python manage.py migrate --no-input

# 6. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "   Next steps:"
echo "   1. Edit .env and add your OPENAI_API_KEY"
echo "   2. (Optional) Train the model: cd utils && python train_model.py"
echo "   3. Start server: python manage.py runserver"
echo "   4. Open: http://127.0.0.1:8000/"
echo ""
