from django.http import JsonResponse
from django.views.decorators.http import require_GET
import psycopg2
from django.db import connection
import socket

@require_GET
def health_check(request):
    """Comprehensive health check for Railway"""
    checks = {}
    
    # 1. Basic app status
    checks['app'] = 'running'
    
    # 2. Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks['database'] = 'connected'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
    
    # 3. Cache check (if using)
    checks['cache'] = 'not_configured'
    
    # 4. External services (if any)
    checks['external_services'] = 'none'
    
    # Overall status
    overall = 'healthy' if checks.get('database') == 'connected' else 'unhealthy'
    
    return JsonResponse({
        'status': overall,
        'timestamp': '2024-01-01T00:00:00Z',  # You can import timezone
        'service': 'Social Media API',
        'version': '1.0.0',
        'checks': checks
    }, status=200 if overall == 'healthy' else 503)