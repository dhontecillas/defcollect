import os

def setup_default_env():
    default_env  = { 'DB_HOST':'localhost',
                     'DB_NAME':'dbname',
                     'DB_USER':'dbuser',
                     'DB_PASS':'dbp4ssword',
                     'DB_PORT':'5555',
                     'APP_NAME':'modelsdefapi',
                   }
    for dkey, dval in default_env.items():
        if dkey not in os.environ:
            os.environ[dkey] = dval
