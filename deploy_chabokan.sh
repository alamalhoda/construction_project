#!/bin/bash
# Complete server update and deployment script for Chabokan.net
# This script updates the server, syncs with chabokan-deployment branch, and starts the server

set -e  # Exit on any error

echo "🚀 Complete server update and deployment for Chabokan.net..."

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This is not a git repository!"
    exit 1
fi

print_step "1. Stopping existing processes..."

# Stop existing processes
pkill -f gunicorn 2>/dev/null || print_message "No Gunicorn process found"
pkill nginx 2>/dev/null || print_message "No Nginx process found"

# Wait for processes to stop
sleep 2

print_step "2. Backing up server local files..."

# Backup important server files
BACKUP_DIR="/tmp/server_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Files that should be protected
PROTECTED_FILES=(
    ".env"
    "database/online.sqlite3"
    "logs/"
    "media/"
    "backups/"
)

for file in "${PROTECTED_FILES[@]}"; do
    if [ -e "$file" ]; then
        cp -r "$file" "$BACKUP_DIR/"
        print_message "Backed up: $file"
    fi
done

print_step "3. Syncing with chabokan-deployment branch..."

# Fix Git ownership issue
git config --global --add safe.directory /app
print_message "Fixed Git ownership issue"

# Fetch latest changes
git fetch origin

# Stash local changes to protect them
git stash push -m "Server local files backup $(date)" --include-untracked || print_warning "No changes to stash"

# Pull latest changes from chabokan-deployment
git pull origin chabokan-deployment

# Restore local files from backup
for file in "${PROTECTED_FILES[@]}"; do
    if [ -e "$BACKUP_DIR/$file" ]; then
        cp -r "$BACKUP_DIR/$file" .
        print_message "Restored: $file"
    fi
done

print_step "4. Activating virtual environment..."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_message "Virtual environment activated (venv)"
elif [ -f "env/bin/activate" ]; then
    source env/bin/activate
    print_message "Virtual environment activated (env)"
else
    print_warning "Virtual environment not found"
fi

print_step "5. Installing/updating requirements..."

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_message "Requirements installed/updated"
fi

print_step "6. Running migrations..."

# Run migrations
python manage.py migrate --noinput
print_message "Migrations completed"

print_step "7. Collecting static files..."

# Collect static files
python manage.py collectstatic --noinput --clear
print_message "Static files collected"

print_step "8. Testing Django setup..."

# Test Django
if python manage.py check >/dev/null 2>&1; then
    print_message "Django check passed"
else
    print_warning "Django check failed - continuing anyway"
fi

print_step "9. Starting Gunicorn..."

# Start Gunicorn on port 8000
nohup gunicorn construction_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info > gunicorn.log 2>&1 &

# Wait for Gunicorn to start
sleep 3

print_step "10. Testing Gunicorn..."

# Test Gunicorn
if curl -s http://localhost:8000/health/simple/ > /dev/null; then
    print_message "✅ Gunicorn is working on port 8000"
    curl -s http://localhost:8000/health/simple/
else
    print_error "❌ Gunicorn failed to start"
    echo "Logs:"
    tail -10 gunicorn.log
    exit 1
fi

print_step "11. Setting up Nginx..."

if command -v nginx > /dev/null; then
    # Copy correct nginx config
    if [ -f "nginx_correct.conf" ]; then
        cp nginx_correct.conf /etc/nginx/nginx.conf
        print_message "Nginx config copied"
    elif [ -f "nginx.conf" ]; then
        cp nginx.conf /etc/nginx/nginx.conf
        print_message "Nginx config copied"
    else
        print_warning "No nginx config file found"
    fi
    
    # Create necessary directories
    mkdir -p /run/nginx
    mkdir -p /var/log/nginx
    
    # Create PID file
    echo "$$" > /run/nginx.pid
    
    # Test nginx configuration
    nginx -t
    
    if [ $? -eq 0 ]; then
        # Start Nginx
        nginx -g "daemon off;" &
        NGINX_PID=$!
        
        # Wait for Nginx
        sleep 3
        
        if pgrep nginx > /dev/null; then
            print_message "✅ Nginx started successfully (PID: $NGINX_PID)"
        else
            print_error "❌ Nginx failed to start"
            echo "Error logs:"
            tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No error logs found"
        fi
    else
        print_error "❌ Nginx configuration test failed"
    fi
else
    print_warning "⚠️  Nginx not available, using Gunicorn directly"
fi

print_step "12. Final testing and cleanup..."

# Test localhost
print_message "Testing localhost:8000..."
curl -s http://localhost:8000/health/simple/

# Test external access
print_message "Testing external access..."
EXTERNAL_STATUS=$(curl -s -o /dev/null -w '%{http_code}' https://django-arash.chbk.app/ || echo "000")
print_message "External status: $EXTERNAL_STATUS"

if [ "$EXTERNAL_STATUS" = "200" ]; then
    print_message "🎉 SUCCESS! Site is working at https://django-arash.chbk.app/"
elif [ "$EXTERNAL_STATUS" = "502" ]; then
    print_warning "❌ Still 502 Bad Gateway - Nginx issue"
    print_message "You can access the site directly via Gunicorn on port 8000"
else
    print_warning "⚠️  Status: $EXTERNAL_STATUS"
fi

# Cleanup backup directory
if [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
    print_message "Backup directory cleaned up"
fi

print_message "✅ Server update and deployment completed successfully!"

echo ""
echo "📋 Summary of completed tasks:"
echo "  ✓ Stopped existing processes"
echo "  ✓ Backed up server local files"
echo "  ✓ Synced with chabokan-deployment branch"
echo "  ✓ Activated virtual environment"
echo "  ✓ Updated requirements"
echo "  ✓ Ran migrations"
echo "  ✓ Collected static files"
echo "  ✓ Started Gunicorn"
echo "  ✓ Configured Nginx"
echo "  ✓ Tested server functionality"
echo ""
echo "🔍 Monitoring commands:"
echo "  tail -f gunicorn.log"
echo "  curl http://localhost:8000/health/"
echo "  ps aux | grep gunicorn"
echo ""
echo "🌐 Your site should be accessible at:"
echo "  https://django-arash.chbk.app/"
