import os
import django
from django.db import connections

# Manually override settings for test
from django.conf import settings
if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'global_security',
                'USER': 'root',
                'PASSWORD': 'hola123',
                'HOST': 'localhost',
                'PORT': '3306',
                'OPTIONS': {'charset': 'latin1'},
            }
        },
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth'],
    )
    django.setup()

def check_latin1():
    conn = connections['default']
    with conn.cursor() as cursor:
        cursor.execute("SELECT Nombre FROM menus WHERE Nombre LIKE '%PESTA%A%' LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"Latin1 result: {row[0]}")
            print(f"Hex: {row[0].encode('utf-8').hex() if isinstance(row[0], str) else row[0].hex()}")

if __name__ == "__main__":
    check_latin1()
