from .models import SiteConfiguration

def site_config(request):
    try:
        config = SiteConfiguration.objects.first()
        if not config:
            config = SiteConfiguration.objects.create(site_name="Django E-commerce")
    except Exception:
        config = None
    return {
        'site_config': config
    }
