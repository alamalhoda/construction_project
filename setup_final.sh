#!/bin/bash
# Final setup script for Chabokan.net

echo "🚀 Final setup for Chabokan.net..."

# 1. Stop existing processes
echo "1. Stopping existing processes..."
pkill -f gunicorn 2>/dev/null || echo "No Gunicorn process found"
pkill nginx 2>/dev/null || echo "No Nginx process found"

# 2. Wait
sleep 2

# 3. Start Gunicorn on port 8000 (as it's working)
echo "2. Starting Gunicorn on port 8000..."
nohup gunicorn construction_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 > gunicorn.log 2>&1 &

# 4. Wait for Gunicorn
sleep 3

# 5. Test Gunicorn
echo "3. Testing Gunicorn..."
if curl -s http://localhost:8000/health/simple/ > /dev/null; then
    echo "✅ Gunicorn is working on port 8000"
    curl -s http://localhost:8000/health/simple/
else
    echo "❌ Gunicorn failed to start"
    echo "Logs:"
    tail -10 gunicorn.log
fi

# 6. Setup Nginx
echo "4. Setting up Nginx..."
if command -v nginx > /dev/null; then
    # Copy final nginx config
    cp nginx_final.conf /etc/nginx/sites-available/default
    
    # Start Nginx
    nginx -t && nginx -s reload
    
    if pgrep nginx > /dev/null; then
        echo "✅ Nginx started with correct configuration"
    else
        echo "❌ Nginx failed to start"
    fi
else
    echo "⚠️  Nginx not available, using Gunicorn directly"
fi

# 7. Final test
echo "5. Final test..."
echo "Testing localhost:8000..."
curl -s http://localhost:8000/health/simple/

echo "Testing external access..."
curl -s -o /dev/null -w "Status: %{http_code}\n" https://django-arash.chbk.app/

echo "🎉 Setup completed!"
echo "Your site should be available at: https://django-arash.chbk.app/"
