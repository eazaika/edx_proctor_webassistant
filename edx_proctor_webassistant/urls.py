"""edx_proctor_webassistant URL Configuration

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
from functools import update_wrapper
from rest_framework.routers import DefaultRouter
from social_django.views import complete
from social_core.utils import setting_name

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.admin import site as admin_site

from journaling.api_views import JournalingViewSet
from person.api_views import PermissionViewSet
from proctoring import api_edx_views, api_ui_views
from sso_auth.decorators import set_token_cookie
from ui.views import Index, logout, login as login_view


def wrap_admin(view, cacheable=False):
    def wrapper(*args, **kwargs):
        return admin_site.admin_view(view, cacheable)(*args, **kwargs)
    wrapper.admin_site = admin_site
    return update_wrapper(wrapper, view)

router = DefaultRouter()
router.register(r'exam_register', api_edx_views.ExamViewSet,
                base_name="exam-register")
router.register(r'event_session', api_ui_views.EventSessionViewSet,
                base_name="event-session")
router.register(r'archived_event_session',
                api_ui_views.ArchivedEventSessionViewSet,
                base_name="archived-event-session")
router.register(r'archived_event_session_all',
                api_ui_views.ArchivedEventSessionAllViewSet,
                base_name="archived-event-session-all")
router.register(r'journaling', JournalingViewSet,
                base_name="journaling")
router.register(r'permission', PermissionViewSet,
                base_name="permission")

urlpatterns = [
    url(r'^$', Index.as_view(), name="index"),
    url(r'index/?$', Index.as_view()),
    url(r'^grappelli/', include('grappelli.urls')),

    # admin urls
    url(r'^admin/login/$', set_token_cookie(admin_site.login),
        name='admin:login'),
    url(r'^admin/logout/$', set_token_cookie(wrap_admin(admin_site.logout)),
        name='logout'),
    url(r'^admin/', admin.site.urls),

    url(r'^api/$', api_edx_views.APIRoot.as_view()),
    url(r'^api/', include('proctoring.urls')),
    url(r'^api/', include(router.urls)),
    # few angular views
    url(r'^session/', Index.as_view()),
    url(r'^archive/', Index.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if not settings.SSO_ENABLED:
    urlpatterns += [
        url(r'^login/$', set_token_cookie(login_view), name='login'),
        url(r'^logout/$', set_token_cookie(auth_views.logout),
            {'next_page': '/'}, name='logout')
    ]
else:
    extra = getattr(settings, setting_name('TRAILING_SLASH'),
                    True) and '/' or ''
    urlpatterns += [
        url(r'^complete/(?P<backend>[^/]+){0}$'.format(extra),
            set_token_cookie(complete), name='complete'),
        url('', include('social_django.urls', namespace='social')),
        url(r'^logout/$', logout, name='logout'),
    ]
