from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse
import os

def serve_frontend(request, path=''):
    """Serve frontend files from the frontend directory"""
    # Try to find frontend folder relative to backend
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'frontend')
    frontend_dir = os.path.normpath(frontend_dir)
    
    if not path or path == '/':
        file_path = os.path.join(frontend_dir, 'index.html')
    else:
        file_path = os.path.join(frontend_dir, path.lstrip('/'))
    
    if os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
        }
        content_type = content_types.get(ext, 'text/plain')
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type=content_type)
    
    # Try as directory index
    index_path = os.path.join(frontend_dir, path.lstrip('/'), 'index.html')
    if os.path.isfile(index_path):
        with open(index_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    # Fallback to frontend index.html (SPA style)
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.isfile(index_path):
        with open(index_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse('Frontend not found. Make sure frontend/ folder is next to backend/', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve frontend in development
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^(?P<path>.*)$', serve_frontend),
    ]
