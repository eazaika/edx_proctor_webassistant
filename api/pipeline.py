import logging

from django.db import transaction

from api.models import Permission
from social.pipeline import partial

log = logging.getLogger(__name__)


@transaction.atomic
def set_roles_for_edx_users(user, permissions):
    '''
    This function create roles for proctors from sso permissions.
    '''

    permission_list = []
    for role in permissions:
        if role['obj_perm'] in ([u'Proctoring'], [u'*']):
            permission_list.append(Permission(
                object_type=role['obj_type'],
                object_id=role['obj_id'],
                user=user
            )
            )
    Permission.objects.filter(user=user).delete()
    Permission.objects.bulk_create(permission_list)


@partial.partial
def create_or_update_permissions(backend, user, response, *args, **kwargs):
    permissions = response.get('permissions')
    if permissions is not None:
        try:
            set_roles_for_edx_users(user, permissions)
        except Exception as e:
            print e
            log.error(u'set_roles_for_edx_users error: {}'.format(e))

    return response
