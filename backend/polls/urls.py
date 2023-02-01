from django.urls import path

from . import views

urlpatterns = [
    path('answer', views.index, name='index'),
    path('get_token', views.get_csrf_token, name='get_token'),
    path('get_domains', views.get_domains, name='get_domains'),
    path('x', views.x, name='x'),
]