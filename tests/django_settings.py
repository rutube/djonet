
MONETDB_HOSTNAME = 'localhost'
MONETDB_PORT = 50000
MONETDB_PASSPHRASE = 'testdb'


DATABASES = {
    'default': {
        'ENGINE': 'djonet',
        'NAME': 'djonet',
        'USER': 'monetdb',
        'PASSWORD': 'monetdb',
        'HOST': MONETDB_HOSTNAME,
        'PORT': MONETDB_PORT,
    }
}


SECRET_KEY = 'djonetrules'
