# coding: utf-8
from django.conf.urls import url
from .views import home, new_buchette, accept_buchette, deny_buchette, singup_view, buchette_payees, \
    confirmation_buchette_soldees, buchette_non_payee
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    url(r'home$', home, name="player_home"),
    url(r'login$', LoginView.as_view(template_name="buchettes_app/login_form.html"),
         name="player_login"),
    url(r'logout$', LogoutView.as_view(),name="player_logout"),
    url(r'new_buchette', new_buchette, name="new_buchette"),
    url(r'buchette_payees', buchette_payees, name="buchette_payees"),
    url(r'accept_buchette/(?P<id>\d+)/$', accept_buchette, name="accept_buchette"),
    url(r'deny_buchette/(?P<id>\d+)/$', deny_buchette, name="deny_buchette"),
    url(r'confirmation_buchette_soldees/(?P<user_id>\d+)/$', confirmation_buchette_soldees,
        name="confirmation_buchette_soldees"),
    url(r'buchette_non_payee/(?P<user_id>\d+)/$', buchette_non_payee,
        name="buchette_non_payee"),
    url(r'signup$', singup_view, name='player_signup')
    ]

urlpatterns += staticfiles_urlpatterns()

