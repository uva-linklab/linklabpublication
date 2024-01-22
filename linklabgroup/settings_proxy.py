from .settings import *

# Check to see if MySQLdb is available; if not, have pymysql masquerade as
# MySQLdb. This is a convenience feature for developers who cannot install
# MySQLdb locally; when running in production on Google App Engine Standard
# Environment, MySQLdb will be used.
try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql

    pymysql.install_as_MySQLdb()

# [START db_setup]
if os.getenv('GAE_APPLICATION', None):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": "/cloudsql/linklabpublication:us-central1:linklabpublication",
            "NAME": "milestone",
            "USER": "fengyi",
            "PASSWORD": "linklab1234qwer1234qwer",
        }
    }
else:
    # Running locally so connect to either a local MySQL instance or connect to
    # Cloud SQL via the proxy. To start the proxy via command line:
    #
    #     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    #
    # See https://cloud.google.com/sql/docs/mysql-connect-proxy
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": "127.0.0.1",
            "PORT": "3306",
            "NAME": "milestone",
            "USER": "fengyi",
            "PASSWORD": "linklab1234qwer1234qwer",
        }
    }
# [END db_setup]