#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/ItemCatalogApp/")

from catalog import app as application
application.secret_key = 'DunYbdwXfcdWd_NzzSX7vciP'
