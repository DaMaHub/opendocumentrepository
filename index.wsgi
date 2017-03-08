import sys, os, bottle

sys.path = ['/var/wsgi/odr/'] + sys.path
os.chdir('/var/wsgi/odr/')

import odr # This loads your application

application = odr.app