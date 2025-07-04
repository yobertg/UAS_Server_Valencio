"""
Django settings for simplelms project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--au_k(pz^loe(+%yeeo$#0m#@-p0+z*notwvk$nya(=r@2==$%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lms_core',
    'ninja',
    'ninja_simple_jwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'ninja.compatibility.files.fix_request_files_middleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'simplelms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'simplelms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Configuration with your RSA keys
NINJA_SIMPLE_JWT = {
    # Use your provided RSA keys directly in settings
    'JWT_PRIVATE_KEY': """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAteLD7H27e4G35qWpNmII3h84UViYbHU1dxmaT0+Twp0k/+XD
tThn0Dw71APW+LG6Q/u0ywkIkWpysmTRo1q/uXNEjkjqOZsIvrKpULBdadHy4qwP
+6ELlLTp/BCGmlL9fkV+DQGudQwfXbp2WsEzKaH/Da/LCNScWLiJ9tIxSqS3Hh1V
f/xKP3mKIH2/8HQH0iSluKvyZg7vdn1sxstlbesBSBmGYw1QLl2VPQEmfGzsYeSi
EqShKUBBJp9xrrFUWiGpynMIZmj+JNjLzpB8heRt2s+JALNIWbFfQ4j5CWZPFazR
Qx+/R2vZlCgvmrskqxA7qYGK9XL4jfRlAFkLEwIDAQABAoIBAAWaP0QefvMBd/6X
SLyMZxu5PqnAZSvy4LUGXJEn16dte4r6v702+3k+RohNa/nYg6IxDSZNGDuRpogy
Zp2Cn8tte2wEkls4fs72jHrLS/CEz1eTF26K5q/rpXxAFN1V3bARIbfypTYlK79e
QH089gxiWVhjFPAOZUuut4IBguCUX/3wBMwZe/W73YznQp2fEltz1m1fjx1Sxtd9
YplFOvDooOWpb+Chne5MzJreQvuqBQ9FOeZyrMAsUDXkAjksmyGR4zPg0/IA660M
N1DDEP0PEPkowwNdDeAHussJmPVR3ZX8HodbggJnRX29S2zGNJSjLjFQBLxQrDTw
NCBmjNECgYEA3eB75jqFNbyWA5VQpW5N52pIKgCflx9mYVE53MoDgYtNZf5DcW2u
FLAQASudd8apVVKuGXQz1H7m40Tj2VeDFV66E99O3o9ixz/v7gcq8Yhvav2IrxXL
anxOOYaBG2hhWTqn1gWU5vNr3dPmiIY7x/7l0r3E2mEbByYUH8GxYTECgYEA0dvK
wk6ZH0nH9UgnSwRmx3r/iY2RNW/WDEeAF6Vz7MuaS8bvKSa90/XFXdVl1PD16C8L
kp164aJqQq36OhTnXmwgovJaZh+auq8Ae9sOH5m8bc25kimyFG9ZlSlejngk5DjS
xh7v+88wlE6lNNZHUNkWlcAmS2pasSxFozntf4MCgYBlCZjiWrvWoK5fq1syOmzX
eRqrpeUG2JGyt152ILhAAcOZMpRbzup7GUHwhoAKzzjFVgVaKgSAO9nAnNp1Wtii
nqR18DbmOr1spr0H09PGca7rNdFMicw8DadBovKgHIRYMdHEMH6CPU9dkOVmPlpy
1Kyrryc5mwbH1ptLatTvwQKBgQCUdsXuyOQS+oN3x1/k9mwv25hEm96Ky1/GuB6q
m+ZzM2cpDMfNeRb6iPjj9UBhcUbGx+GMC9UPI3PBUIuh43/7kMtV+9ZwQROZ1oyl
EsffG0fu9oe+G7lcM5pQqD+40s5mlrymZOSqZF2dzjWaN62kSLBtqM5utAMNLKDn
ZOfcOQKBgQDNEDcLgn9VjFXdI+B4EOJ5nYLt+QISrhApOEn8B6mQ3rHdLH7Euop8
lNYw7k+sniXuHrzrxhdz6ru0hOyTyHF61KfU4uqFzz2YtfXLYE4kEB7cY3373MjY
/8p3PXG6U3nL6OspJtJWM7+rw6SJXdw05trD2ydd6KP4nBhvuz+/5g==
-----END RSA PRIVATE KEY-----""",
    
    'JWT_PUBLIC_KEY': """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAteLD7H27e4G35qWpNmII
3h84UViYbHU1dxmaT0+Twp0k/+XDtThn0Dw71APW+LG6Q/u0ywkIkWpysmTRo1q/
uXNEjkjqOZsIvrKpULBdadHy4qwP+6ELlLTp/BCGmlL9fkV+DQGudQwfXbp2WsEz
KaH/Da/LCNScWLiJ9tIxSqS3Hh1Vf/xKP3mKIH2/8HQH0iSluKvyZg7vdn1sxstl
besBSBmGYw1QLl2VPQEmfGzsYeSiEqShKUBBJp9xrrFUWiGpynMIZmj+JNjLzpB8
heRt2s+JALNIWbFfQ4j5CWZPFazRQx+/R2vZlCgvmrskqxA7qYGK9XL4jfRlAFkL
EwIDAQAB
-----END PUBLIC KEY-----""",
    
    # JWT Settings
    'ACCESS_TOKEN_LIFETIME_MINUTES': 60,  # 1 hour
    'REFRESH_TOKEN_LIFETIME_MINUTES': 60 * 24 * 7,  # 7 days
    'ALGORITHM': 'RS256',  # RSA with SHA-256
    
    # Token claims mapping
    'TOKEN_CLAIM_USER_ATTRIBUTE_MAP': {
        'user_id': 'id',
        'username': 'username',
        'email': 'email',
        'first_name': 'first_name',
        'last_name': 'last_name',
    },
    
    # Other settings
    'WEB_REFRESH_COOKIE_PATH': '/api/auth/web/token-refresh',
    'WEB_REFRESH_COOKIE_NAME': 'refresh',
}

try:
    from .local_settings import *
except:
    pass