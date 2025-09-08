#!/bin/bash
# Test script for correct domain configuration

echo "🧪 Testing correct domain configuration..."

# Test 1: Check Gunicorn on port 8000
echo "1. Testing Gunicorn on port 8000..."
if curl -s http://localhost:8000/health/simple/ > /dev/null; then
    echo "✅ Gunicorn is working on port 8000"
    curl -s http://localhost:8000/health/simple/
else
    echo "❌ Gunicorn is not working on port 8000"
fi

# Test 2: Check Nginx on port 80
echo "2. Testing Nginx on port 80..."
if pgrep nginx > /dev/null; then
    echo "✅ Nginx is running"
    if curl -s http://localhost:80/health/simple/ > /dev/null; then
        echo "✅ Nginx responds on port 80"
        curl -s http://localhost:80/health/simple/
    else
        echo "❌ Nginx does not respond on port 80"
    fi
else
    echo "❌ Nginx is not running"
fi

# Test 3: Check external access to correct domain
echo "3. Testing external access to https://django-arash.chbk.app/..."
EXTERNAL_STATUS=$(curl -s -o /dev/null -w '%{http_code}' https://django-arash.chbk.app/)
echo "External status: $EXTERNAL_STATUS"

if [ "$EXTERNAL_STATUS" = "200" ]; then
    echo "🎉 SUCCESS! Site is working at https://django-arash.chbk.app/"
    echo "Testing health check..."
    curl -s https://django-arash.chbk.app/health/simple/
elif [ "$EXTERNAL_STATUS" = "502" ]; then
    echo "❌ 502 Bad Gateway - Nginx configuration issue"
    echo "Gunicorn is working but Nginx can't connect to it"
elif [ "$EXTERNAL_STATUS" = "000" ]; then
    echo "❌ Connection failed - Server or domain issue"
else
    echo "⚠️  Status: $EXTERNAL_STATUS"
fi

# Test 4: Check ports
echo "4. Checking ports..."
echo "Port 8000 (Gunicorn):"
netstat -tlnp | grep :8000 || echo "Port 8000 not listening"

echo "Port 80 (Nginx):"
netstat -tlnp | grep :80 || echo "Port 80 not listening"

# Test 5: Check processes
echo "5. Checking processes..."
echo "Gunicorn processes:"
ps aux | grep gunicorn | grep -v grep || echo "No Gunicorn processes"

echo "Nginx processes:"
ps aux | grep nginx | grep -v grep || echo "No Nginx processes"

echo "🧪 Test completed!"
