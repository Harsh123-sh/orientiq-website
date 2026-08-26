import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "orientiq.settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application