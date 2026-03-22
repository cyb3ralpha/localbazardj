#!/bin/bash
echo "🛒 Local Bazar Setup"
echo "===================="
cd backend
python -m venv venv
source venv/bin/activate 2>/dev/null || venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Demo credentials:"
echo "   Admin:    admin / admin123"
echo "   Seller:   seller1 / seller123"
echo "   Employee: employee1 / emp123"
echo ""
echo "▶️  Start backend:  python manage.py runserver"
echo "▶️  Open frontend:  open http://127.0.0.1:5500 (use Live Server)"
