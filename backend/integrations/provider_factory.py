from django.conf import settings
from django.utils.module_loading import import_string

from .base import ProviderUnavailable


def get_authorized_provider():
    class_path = settings.RAILWAY_PROVIDER_CLASS.strip()
    if not class_path:
        raise ProviderUnavailable("No authorized railway information provider is configured.")
    provider_class = import_string(class_path)
    provider = provider_class()
    if not getattr(provider, "authorized", False):
        raise ProviderUnavailable("The configured provider has not declared authorized access.")
    return provider
