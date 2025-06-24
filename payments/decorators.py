import ipaddress
from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden


def get_client_ip(request):
    """
    Надежно получает IP-адрес клиента, учитывая наличие reverse-proxy.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def yookassa_ip_check(view_func):
    """
    Декоратор, который проверяет, пришел ли запрос с доверенного IP-адреса ЮKassa.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        client_ip_str = get_client_ip(request)
        if not client_ip_str:
            return HttpResponseForbidden("Could not determine client IP.")

        client_ip = ipaddress.ip_address(client_ip_str)
        is_allowed = False
        for allowed_network in settings.YOOKASSA_WEBHOOK_IPS:
            if client_ip in ipaddress.ip_network(allowed_network):
                is_allowed = True
                break

        if not is_allowed:
            print(f"WARNING: Forbidden webhook access attempt from IP: {client_ip}")
            return HttpResponseForbidden("Forbidden: IP address not allowed.")

        return view_func(request, *args, **kwargs)
    return _wrapped_view