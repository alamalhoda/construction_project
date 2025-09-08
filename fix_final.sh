#!/bin/bash
# Final fix for Chabokan.net - Correct domain and port configuration

echo "🔧 Final fix for Chabokan.net..."

# 1. Stop existing processes
echo "1. Stopping existing processes..."
pkill -f gunicorn 2>/dev/null || echo "No Gunicorn process found"
pkill nginx 2>/dev/null || echo "No Nginx process found"

# 2. Wait
sleep 2

# 3. Start Gunicorn on port 8000 (as it's working)
echo "2. Starting Gunicorn on port 8000..."
nohup gunicorn construction_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info > gunicorn.log 2>&1 &

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
    exit 1
fi

# 6. Setup Nginx with correct configuration
echo "4. Setting up Nginx..."
if command -v nginx > /dev/null; then
    # Copy correct nginx config
    cp nginx_correct.conf /etc/nginx/nginx.conf
    
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
            echo "✅ Nginx started successfully (PID: $NGINX_PID)"
        else
            echo "❌ Nginx failed to start"
            echo "Error logs:"
            tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No error logs found"
        fi
    else
        echo "❌ Nginx configuration test failed"
    fi
else
    echo "⚠️  Nginx not available, using Gunicorn directly"
fi

# 7. Final test
echo "5. Final test..."
echo "Testing localhost:8000..."
curl -s http://localhost:8000/health/simple/

echo "Testing external access..."
EXTERNAL_STATUS=$(curl -s -o /dev/null -w '%{http_code}' https://django-arash.chbk.app/)
echo "External status: $EXTERNAL_STATUS"

if [ "$EXTERNAL_STATUS" = "200" ]; then
    echo "🎉 SUCCESS! Site is working at https://django-arash.chbk.app/"
elif [ "$EXTERNAL_STATUS" = "502" ]; then
    echo "❌ Still 502 Bad Gateway - Nginx issue"
    echo "Trying direct Gunicorn approach..."
    echo "You can access the site directly via Gunicorn on port 8000"
else
    echo "⚠️  Status: $EXTERNAL_STATUS"
fi

echo "🔧 Fix completed!"
