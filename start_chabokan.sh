#!/bin/bash
# Start script for Chabokan.net deployment
# This script starts the Django application with proper configuration

set -e  # Exit on any error

echo "🚀 Starting Django application on Chabokan.net..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Set Django settings
export DJANGO_SETTINGS_MODULE=construction_project.settings_chabokan
print_info "Django settings module: $DJANGO_SETTINGS_MODULE"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f ".env.chabokan" ]; then
        cp .env.chabokan .env
        print_warning "Please update .env file with your actual values!"
    else
        print_error ".env.chabokan template not found!"
        exit 1
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    print_info "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check database connection
print_info "Checking database connection..."
python manage.py check --database default

# Run migrations if needed
print_info "Running database migrations..."
python manage.py migrate

# Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput

# Check security settings
print_info "Running security checks..."
python security_chabokan.py

# Get port from environment or use default
PORT=${PORT:-8000}
print_info "Starting server on port $PORT"

# Start the application
print_status "Starting Django application with Gunicorn..."

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    print_error "Gunicorn not found. Installing..."
    pip install gunicorn
fi

# Start with Gunicorn
exec gunicorn --config gunicorn.conf.py wsgi_chabokan:application
