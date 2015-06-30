from django.conf.urls import patterns, url

urlpatterns = patterns(
    'tracking.views',
    url(r'^$', 'dashboard', name='tracking-dashboard'),
    url(r'^show-light-box/$', 'show_light_box', name='show_light_box'),
)
