import os
PWD = os.path.abspath(os.curdir)

DEBUG=True
SECRET_KEY = 'thisissecret'
CSRF_ENABLED = True
SESSION_PROTECTION = 'strong'

MONGO_URI = 'mongodb://recipe:transform@ds043447.mongolab.com:43447/recipe'
