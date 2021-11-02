"""grape URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^user-edit/$', views.user_edit, name='user_edit'),
    url(r'^add-user/$', views.add_user, name='add_user'),
    url(r'^long-poll/$', views.long_poll, name='long_poll'),
    url(r'^axios-test/$', views.axios_test, name='axios_test'),
    url(r'^add-user-new/$', views.add_user_new, name='add_user_new'),
    url(r'^update-user/$', views.update_user, name='update_user'),
    url(r'^update-user-new/$', views.update_user_new, name='update_user_new'),
    url(r'^get-user/$', views.get_user, name='get_user'),
    url(r'^get-user-new/$', views.get_user_new, name='get_user_new'),
    url(r'^get-file/$', views.get_file, name='get_file'),
    url(r'^test-file/$', views.test_file, name='test_file'),
    url(r'^delete-file/$', views.delete_file, name='delete_file'),
    url(r'^get-user-cookie/$', views.get_user_cookie, name='get_user_cookie'),
    url(r'^get-user-cookie-new/$', views.get_user_cookie_new, name='get_user_cookie_new'),
    url(r'^test/$', views.test, name='test'),
    url(r'^multi-list/$', views.multiList, name='multiList'),
    url(r'^multi-list-test/$', views.multiList_test, name='multiList_test'),
    url(r'^$', views.mix, name='mix'),
]
