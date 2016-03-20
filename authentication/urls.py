"""authentication URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.contrib.auth import views
from django.contrib.auth.decorators import user_passes_test

from .forms import LoginForm
from .views import RegistrationFormView

#login_forbidden =  user_passes_test(lambda u: u.is_anonymous(), '/')

urlpatterns = [
    url(r'^login/$', views.login, {'template_name': 'login_form.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout_then_login, name='logout'),
    url(r'^register/$', RegistrationFormView.as_view(), name='register'),
]
