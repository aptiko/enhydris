from django.conf.urls.defaults import include, patterns
from django.contrib.auth.views import password_reset, password_reset_done, \
                                      password_change, password_change_done
from django.contrib import admin
from registration.views import register
from profiles.views import create_profile, edit_profile
from enhydris.hcore.forms import HcoreRegistrationForm
from enhydris.hcore.views import terms, profile_view, login

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/login/$', login, {'template_name': 'registration/login.html'}),
    (r'^accounts/register/$', register, {'form_class':
        HcoreRegistrationForm}, 'registration_register'),
    (r'^accounts/password/reset/$', password_reset, {'template_name':
        'registration/password_reset.html'}, 'password_reset'),
    (r'^accounts/password/reset/done/$', password_reset_done,
        {'template_name': 'registration/password_reset_done.html'},
        'password_reset_done'),
    (r'^accounts/password/change/$', password_change, {'template_name':
        'registration/password_change.html'}, 'password_change'),
    (r'^accounts/password/change/done/$', password_change_done,
        {'template_name': 'registration/password_change_done.html'},
        'password_change_done'),


    (r'^accounts/', include('registration.urls')),

    # django profiles
    # to enable django <-> site admin overlapping
    #(r'^profiles/admin/(.*)', admin.site.root),
    #(r'^profile/', include('profiles.urls')),
    (r'^profile/create/$', create_profile, {}, 'profiles_create_profile'),
    (r'^profile/edit/$', edit_profile, {}, 'profiles_edit_profile'),
    (r'^profile/(?P<username>\w+)/$', profile_view, {},
                                 'profiles_profile_detail'),


    # terms of usage
    (r'^terms/$', terms,{}, 'terms'),

    # internationalization
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^ajax/', include('ajax_select.urls')),
    (r'^api/', include('enhydris.api.urls')),
    (r'', include('enhydris.hcore.urls')),
)
