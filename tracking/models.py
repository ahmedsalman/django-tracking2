import logging

from django.utils import timezone
from django.contrib.gis.geoip import HAS_GEOIP
if HAS_GEOIP:
    from django.contrib.gis.geoip import GeoIP, GeoIPException
from django.db import models
from django.conf import settings
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_save
from tracking.managers import VisitorManager, PageviewManager
from tracking.settings import TRACK_USING_GEOIP
from .compat import User

GEOIP_CACHE_TYPE = getattr(settings, 'GEOIP_CACHE_TYPE', 4)

log = logging.getLogger(__file__)


class Visitor(models.Model):
    session_key = models.CharField(max_length=72)
    cookie_key = models.CharField(max_length=72)
    user = models.ForeignKey(User, related_name='visit_history',
                             null=True, editable=False)
    # Update to GenericIPAddress in Django 1.4
    ip_address = models.CharField(max_length=39, editable=False)
    user_agent = models.TextField(null=True, editable=False)
    start_time = models.DateTimeField(default=timezone.now, editable=False)
    expiry_age = models.IntegerField(null=True, editable=False)
    expiry_time = models.DateTimeField(null=True, editable=False)
    time_on_site = models.IntegerField(null=True, editable=False)
    end_time = models.DateTimeField(null=True, editable=False)

    objects = VisitorManager()

    def session_expired(self):
        "The session has ended due to session expiration"
        if self.expiry_time:
            return self.expiry_time <= timezone.now()
        return False
    session_expired.boolean = True

    def session_ended(self):
        "The session has ended due to an explicit logout"
        return bool(self.end_time)
    session_ended.boolean = True


    class Meta(object):
        ordering = ('-start_time',)


class Pageview(models.Model):
    visitor = models.ForeignKey(Visitor, related_name='pageviews')
    url = models.TextField(null=False, editable=False)
    referer = models.TextField(null=True, editable=False)
    query_string = models.TextField(null=True, editable=False)
    method = models.CharField(max_length=20, null=True)
    view_time = models.DateTimeField()

    objects = PageviewManager()

    class Meta(object):
        ordering = ('-view_time',)
