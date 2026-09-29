from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import DefaultRouter

from hello_app.api import NoteViewSet

# REST API (урок 35): роутер будує /api/notes/ і /api/notes/<id>/ з NoteViewSet
router = DefaultRouter()
router.register("notes", NoteViewSet, basename="note")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Django built-in auth: login, logout, password change
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", include("hello_app.urls", namespace="hello_app")),
] + debug_toolbar_urls()
