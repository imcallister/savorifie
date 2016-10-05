#!/bin/sh

if [ ! -z "$ACCOUNTIFIE_MIGRATE" ]; then
  su accountifie -c "cd /savorifie && python manage.py migrate && python manage.py loaddata base_company environment user && python manage.py runserver $LISTEN_ADDR"
else
  su accountifie -c "cd /savorifie && python manage.py runserver $LISTEN_ADDR"
fi

