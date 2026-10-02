"""Presentation routes; upstream voting endpoints remain unchanged."""
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, re_path
from django.views.static import serve
from urls import urlpatterns as upstream_patterns
from helios.models import Election
UI = Path(__file__).parent / 'ui'
def home(request):
    elections = Election.objects.filter(private_p=False, archived_at__isnull=True, deleted_at__isnull=True, frozen_at__isnull=False).exclude(uuid='').order_by('-created_at')[:20]
    return render(request, 'home_demo.html', {'elections': elections})
def booth(request):
    return HttpResponse((Path(settings.ROOT_PATH) / 'heliosbooth/vote.html').read_text())
urlpatterns = [path('', home), path('booth/vote.html', booth),
    re_path(r'^demo-ui/(?P<path>.*)$', serve, {'document_root': str(UI / 'assets')})] + upstream_patterns
