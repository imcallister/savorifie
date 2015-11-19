from django.db.models.signals import pre_syncdb, post_syncdb
from django.contrib.auth import models as auth_models
from django.db import connection


def update_auth_perm_length(sender, **kwargs):
  cursor = connection.cursor()
  cursor.execute("UPDATE pg_attribute SET atttypmod = 100+4 WHERE attrelid = 'auth_permission'::regclass AND attname = 'name'")

post_syncdb.connect(update_auth_perm_length, sender=auth_models)