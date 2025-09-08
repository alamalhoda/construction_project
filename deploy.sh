#!/bin/bash
# Deployment script for Chabokan.net
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting Chabokan.net deployment..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not activated. Activating..."
    source env/bin/activate 2>/dev/null || {
        print_error "Virtual environment not found. Please create one first."
        exit 1
    }
fi

# Install requirements
print_status "Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Please create one with your configuration!"
    print_warning "You can copy from .env.chabokan template if available."
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
print_status "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@chabokan.net', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Run security checks
print_status "Running security checks..."
python security_check.py

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Set permissions
print_status "Setting permissions..."
chmod 755 logs
chmod 755 media
chmod 755 staticfiles

# Test the application
print_status "Testing the application..."
python manage.py check --deploy

print_status "Deployment completed successfully!"
echo "=================================="
print_status "Next steps:"
echo "1. Update .env file with your actual values"
echo "2. Configure your domain in Chabokan.net panel"
echo "3. Upload your code to Chabokan.net"
echo "4. Set up PostgreSQL database in Chabokan.net"
echo "5. Configure Nginx settings"
echo "6. Start your application with: gunicorn --config gunicorn.conf.py"
echo "=================================="
