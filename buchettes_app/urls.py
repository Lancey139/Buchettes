from django.conf.urls import url
from .views import home, new_buchette, accept_buchette, deny_buchette
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    url(r'home$', home, name="player_home"),
    url(r'login$', LoginView.as_view(template_name="buchettes_app/login_form.html"),
         name="player_login"),
    url(r'logout$', LogoutView.as_view(),name="player_logout"),
    url(r'new_buchette', new_buchette, name="new_buchette"),
    url(r'accept_buchette/(?P<id>\d+)/$', accept_buchette, name="accept_buchette"),
    url(r'deny_buchette/(?P<id>\d+)/$', deny_buchette, name="deny_buchette")
    ]

