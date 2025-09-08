# Security Report for Chabokan.net Deployment
==================================================

## Django Version: 4.2.23

## Security Settings
- DEBUG: True
- ALLOWED_HOSTS: ['localhost', '127.0.0.1', '.chabokan.net', '.chabokan.ir', 'localhost']
- SECURE_SSL_REDIRECT: False
- SECURE_HSTS_SECONDS: 31536000
- CSRF_COOKIE_SECURE: False
- SESSION_COOKIE_SECURE: False

## Environment Variables
- SECRET_KEY: your-secre...
- DB_NAME: construction_db
- DB_USER: construction_user
- DB_HOST: localhost
- ALLOWED_HOST: localhost

## Security Recommendations
1. Change the default SECRET_KEY
2. Configure proper ALLOWED_HOSTS
3. Enable SSL/HTTPS
4. Set up proper logging
5. Regular security updates
6. Monitor access logs
