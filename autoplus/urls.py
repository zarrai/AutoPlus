"""autoplus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import path
from controlcenter.views import controlcenter
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('admin/dashboard/', controlcenter.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^cart/', include('shopping_cart.urls', namespace='shopping_cart')),
    #url(r'^', include(('authapp.urls', 'authapp'), namespace='authapp')),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^', include(('main.urls', 'main'), namespace='main')),

    url('avatar/', include('avatar.urls')),
    url('profile/', include('userprofiles2.urls')),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
