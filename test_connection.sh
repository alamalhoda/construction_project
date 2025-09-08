#!/bin/bash
# Test connection script for Chabokan.net

echo "🔍 Testing Chabokan.net connection..."

# Test 1: Check if Gunicorn is running
echo "1. Checking Gunicorn process..."
if pgrep -f gunicorn > /dev/null; then
    echo "✅ Gunicorn is running"
    echo "   PIDs: $(pgrep -f gunicorn)"
else
    echo "❌ Gunicorn is not running"
fi

# Test 2: Check port 3000
echo "2. Checking port 3000..."
if netstat -tlnp | grep :3000 > /dev/null; then
    echo "✅ Port 3000 is listening"
    netstat -tlnp | grep :3000
else
    echo "❌ Port 3000 is not listening"
fi

# Test 3: Test Gunicorn directly
echo "3. Testing Gunicorn directly..."
if curl -s http://localhost:3000/health/simple/ > /dev/null; then
    echo "✅ Gunicorn responds on localhost:3000"
    curl -s http://localhost:3000/health/simple/
else
    echo "❌ Gunicorn does not respond on localhost:3000"
fi

# Test 4: Check Nginx
echo "4. Checking Nginx..."
if pgrep nginx > /dev/null; then
    echo "✅ Nginx is running"
    echo "   PID: $(pgrep nginx)"
else
    echo "❌ Nginx is not running"
fi

# Test 5: Check port 80
echo "5. Checking port 80..."
if netstat -tlnp | grep :80 > /dev/null; then
    echo "✅ Port 80 is listening"
    netstat -tlnp | grep :80
else
    echo "❌ Port 80 is not listening"
fi

# Test 6: Test external access
echo "6. Testing external access..."
if curl -s https://django-arash.chbk.app/health/simple/ > /dev/null; then
    echo "✅ External access works"
    curl -s https://django-arash.chbk.app/health/simple/
else
    echo "❌ External access fails"
    echo "   Status: $(curl -s -o /dev/null -w '%{http_code}' https://django-arash.chbk.app/)"
fi

echo "🔍 Test completed!"
