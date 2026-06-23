from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', '-05sgp9!deq=q1nltm@^^2cc+v29i(tyybv3v2t77qi66czazj')
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'crispy_bootstrap4',
    'django_countries',
    'apps.products',
    'apps.cart',
    'apps.orders',
    'apps.payments',
    'apps.users'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for modern django-allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.products.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.products.context_processors.site_config',
            ],

        },
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'  # Bangladesh timezone
USE_I18N = True
USE_TZ = True

# Restrict country field choices to Bangladesh only
COUNTRIES_ONLY = ['BD']

# Static and media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'static_root'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / 'db.sqlite3'
    }
}

if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Production Email Settings (SMTP)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
else:
    # Development Email Settings (Console - prints emails to stdout)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # Credentials are managed dynamically in the Django admin panel (SocialApp)
    }
}

# Allauth custom settings
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_PREVENT_ENUMERATION = False


# Crispy Forms Config
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Stripe API Keys (set via environment variables)
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Unfold Dynamic Sidebar Lazy Loader
class LazyNavigation(list):
    def __init__(self):
        super().__init__()
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        from django.apps import apps
        
        nav_list = []
        config_items = []
        
        # Group models under custom simple app folders
        for app in apps.get_app_configs():
            # Exclude built-in django applications that don't need grouping
            if app.label in ['admin', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'sites']:
                continue
                
            models = app.get_models()
            items = []
            for model in models:
                model_name = model._meta.model_name
                app_label = app.label
                link = f"/admin/{app_label}/{model_name}/"
                
                # Exclude User model from normal sidebar list to move it to the navbar right corner
                if app_label == 'auth' and model_name == 'user':
                    continue

                # Exclude SiteConfiguration from normal catalog items list
                if model_name == "siteconfiguration":
                    config_items.append({
                        "title": "Website Configuration",
                        "link": link,
                        "icon": "settings",
                    })
                    continue
                
                # Check mapping for icons
                icon = "folder"
                if "user" in model_name:
                    icon = "group"
                elif "item" in model_name or "product" in model_name:
                    icon = "shopping_bag"
                elif "order" in model_name:
                    icon = "receipt"
                elif "payment" in model_name:
                    icon = "credit_card"
                elif "coupon" in model_name:
                    icon = "confirmation_number"
                elif "category" in model_name:
                    icon = "category"
                elif "slide" in model_name:
                    icon = "slideshow"
                elif "address" in model_name:
                    icon = "home"
                elif "refund" in model_name:
                    icon = "assignment_return"
                elif "wishlist" in model_name:
                    icon = "favorite"
                
                items.append({
                    "title": model._meta.verbose_name_plural.capitalize(),
                    "link": link,
                    "icon": icon,
                })
            
            if items:
                nav_list.append({
                    "title": app.verbose_name.capitalize(),
                    "separator": True,
                    "collapsible": True,
                    "items": items,
                })
        
        # Append dynamic dedicated Configuration group at the bottom
        if config_items:
            nav_list.append({
                "title": "Configuration",
                "separator": True,
                "collapsible": False,
                "items": config_items,
            })
        
        self.clear()
        self.extend(nav_list)
        self._loaded = True

    def __iter__(self):
        self._load()
        return super().__iter__()

    def __len__(self):
        self._load()
        return super().__len__()

    def __getitem__(self, index):
        self._load()
        return super().__getitem__(index)


# Django Unfold Theme Settings
UNFOLD = {
    "SITE_TITLE": "Django E-commerce Admin",
    "SITE_HEADER": "Django E-commerce",
    "SITE_SYMBOL": "shopping_cart",  # Material symbols icon
    "SHOW_HISTORY": True,
    "SHOW_SIDEBAR": True,
    "COLLAPSIBLE_SIDEBAR": True,
    "DASHBOARD_CALLBACK": "config.dashboard.dashboard_callback",
    
    # Custom Premium Color Palette (Indigo Theme)
    "COLORS": {
        "primary": {
            "50": "245 243 255",
            "100": "237 233 254",
            "200": "221 214 254",
            "300": "196 181 253",
            "400": "167 139 250",
            "500": "99 102 241",   # Modern Indigo #6366f1
            "600": "79 70 229",
            "700": "67 56 202",
            "800": "55 48 163",
            "900": "49 46 129",
            "950": "17 24 39",
        },
    },
    
    # Custom styling overrides are managed directly in templates/admin/base.html for better maintenance and editing support
    "STYLES": [],
    
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": LazyNavigation(),
    },
    "ACCOUNT": {
        "navigation": [
            {
                "title": "Manage User Accounts",
                "link": "/admin/auth/user/",
                "icon": "group",
            },
        ],
    },
}



