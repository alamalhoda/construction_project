#!/bin/bash
# Restart script for Chabokan.net

echo "🔄 Restarting Chabokan.net application..."

# Stop existing processes
echo "1. Stopping existing processes..."
pkill -f gunicorn 2>/dev/null || echo "No Gunicorn process found"
pkill nginx 2>/dev/null || echo "No Nginx process found"

# Wait a moment
sleep 2

# Test connection
echo "2. Running connection test..."
./test_connection.sh

# Start Gunicorn
echo "3. Starting Gunicorn..."
nohup gunicorn construction_project.wsgi:application --bind 0.0.0.0:3000 --workers 3 > gunicorn.log 2>&1 &

# Wait for Gunicorn to start
sleep 3

# Test Gunicorn
echo "4. Testing Gunicorn..."
if curl -s http://localhost:3000/health/simple/ > /dev/null; then
    echo "✅ Gunicorn is working"
else
    echo "❌ Gunicorn failed to start"
    echo "Logs:"
    tail -10 gunicorn.log
fi

# Start Nginx (if available)
echo "5. Starting Nginx..."
if command -v nginx > /dev/null; then
    nginx -c /app/nginx.conf 2>/dev/null || echo "Nginx config error"
    sleep 2
    
    if pgrep nginx > /dev/null; then
        echo "✅ Nginx started"
    else
        echo "❌ Nginx failed to start"
    fi
else
    echo "⚠️  Nginx not available, using Gunicorn directly"
fi

# Final test
echo "6. Final test..."
./test_connection.sh

echo "🔄 Restart completed!"
