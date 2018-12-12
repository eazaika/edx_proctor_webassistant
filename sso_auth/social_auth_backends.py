"""
Backend for python social auth authentication
"""
import logging

from social_core.utils import handle_http_errors
from social_core.backends.oauth import BaseOAuth2

from django.conf import settings

log = logging.getLogger(__name__)


class TpBackend(BaseOAuth2):
    """
    Backend for authentication usin OAuth2
    """
    name = settings.AUTH_BACKEND_NAME
    ID_KEY = 'username'
    AUTHORIZATION_URL = '{}/oauth2/authorize'.format(settings.SSO_TP_URL)
    ACCESS_TOKEN_URL = '{}/oauth2/access_token'.format(settings.SSO_TP_URL)
    USER_DATA_URL = '{url}/oauth2/access_token/{access_token}/'
    PROFILE_URL = '{}/users/me'.format(settings.SSO_TP_URL)
    DEFAULT_SCOPE = []
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    skip_email_verification = True

    def auth_url(self):
        """
        This function add "auth_entry" get attribute.
        "auth_entry" can be login or register, for correct redirect to login
        or register form on sso-provider.
        """
        return '{}&auth_entry={}'.format(
            super(TpBackend, self).auth_url(),
            self.data.get('auth_entry', 'login')
        )

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        """Completes loging process, must return user instance. """
        self.strategy.session.setdefault('{}_state'.format(self.name),
                                         self.data.get('state'))
        next_url = getattr(settings, 'SOCIAL_NEXT_URL', '/home')
        self.strategy.session.setdefault('next', next_url)
        return super(TpBackend, self).auth_complete(*args, **kwargs)

    def get_user_details(self, response):
        """ Return user details from SSO account. """
        return response

    def user_data(self, access_token, *args, **kwargs):
        """ Grab user profile information from SSO. """
        return self.get_json(
            self.PROFILE_URL,
            params={'access_token': access_token},
            headers={'Authorization': 'Bearer {}'.format(access_token)},
        )

    def do_auth(self, access_token, *args, **kwargs):
        """ Finish the auth process once the access_token was retrieved. """
        data = self.user_data(access_token)
        data['access_token'] = access_token
        kwargs.update(data)
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)
