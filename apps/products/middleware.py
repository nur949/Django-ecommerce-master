from django.shortcuts import render
from .models import SiteConfiguration

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude admin dashboard requests so the admin can always access /admin to turn off maintenance mode
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        try:
            config = SiteConfiguration.objects.first()
            if config and config.maintenance_mode:
                return render(request, 'maintenance.html', {'site_config': config}, status=503)
        except Exception:
            pass

        return self.get_response(request)
