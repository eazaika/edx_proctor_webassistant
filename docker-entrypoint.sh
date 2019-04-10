#!/bin/bash -ex
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>
# v5   add tmp variable $first_run for run Build static and localization

export BIND_ADDR=${BIND_ADDR:-"0.0.0.0"}
export BIND_PORT=${BIND_PORT:-"80"}

echo "EMAIL_HOST - ${EMAIL_HOST}"
echo "EMAIL_PORT - ${EMAIL_PORT}"
echo "EMAIL_USE_TLS - ${EMAIL_USE_TLS}"
echo "EMAIL_HOST_USER - ${EMAIL_HOST_USER}"
echo "EMAIL_HOST_PASSWORD - ${EMAIL_HOST_PASSWORD}"

if [ "${MIGRATION}" == 1 ] || [ "${MIGRATION}" == 'TRUE' ] ||  [ "${MIGRATION}" == 'true' ] || [ "${MIGRATION}" == 'True' ]; then
    echo "start  Build static and localization"
    ./manage.py migrate
    ./manage.py collectstatic
    ./manage.py create_admin_user
    echo "SUPERUSER_USERNAME - $SUPERUSER_USERNAME"
    echo "SUPERUSER_PASSWORD - $SUPERUSER_PASSWORD"
    echo "SUPERUSER_EMAIL - $SUPERUSER_EMAIL"
fi

exec "$@"