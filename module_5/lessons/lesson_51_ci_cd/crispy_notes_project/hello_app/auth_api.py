"""JWT для API нотаток (урок 40): видача токенів з обмеженням спроб.

`TokenObtainPairView` з djangorestframework-simplejwt: POST username + password → access і refresh.
Без обмеження частоти цей ендпоінт — ідеальна ціль для перебору паролів (OWASP A07).
"""
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Не більше 5 спроб входу за хвилину з однієї адреси (REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"])."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
