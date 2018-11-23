import os
import sys
import time_execution
import warnings

from time_execution.backends.elasticsearch import ElasticsearchBackend

from domain.models import Monitor


# Ignore warnings like:
# ...urllib3/connectionpool.py:847: InsecureRequestWarning: Unverified HTTPS
# request is being made...
if not sys.warnoptions:
    msg = r'Unverified HTTPS request is being made.*'
    warnings.filterwarnings('ignore', message=msg, module='.*connectionpool.*')
    # And warnings like:
    # ...http_urllib3.py:135: UserWarning: Connecting to inspire-qa-logs-client1.cern.ch
    # using SSL with verify_certs=False is insecure.
    msg = r'Connecting to .* using SSL with verify_certs=False is insecure.'
    warnings.filterwarnings('ignore', message=msg, module='.*http_urllib3.*')


def configure(env):
    APPMETRICS_ELASTICSEARCH_KWARGS = dict(
        port=443,
        http_auth=(
            os.environ['APPMETRICS_ELASTICSEARCH_USERNAME'],
            os.environ['APPMETRICS_ELASTICSEARCH_PASSWORD']),
        use_ssl=True,
        verify_certs=False,
    )
    APPMETRICS_ELASTICSEARCH_HOSTS = [
        dict(host='inspire-{}-logs-client1.cern.ch'.format(env),
             **APPMETRICS_ELASTICSEARCH_KWARGS),
        dict(host='inspire-{}-logs-client2.cern.ch'.format(env),
             **APPMETRICS_ELASTICSEARCH_KWARGS),
    ]
    INDEX_NAME='inspiremonitoring-{}'.format(env)
    backend = ElasticsearchBackend(
        hosts=APPMETRICS_ELASTICSEARCH_HOSTS,
        index=INDEX_NAME
    )
    time_execution.settings.configure(
        backends=[backend],
        # hooks=(status_code_hook,),
        origin='inspire_next'
    )


def get_env_from_argv(argv):
    try:
        env = sys.argv[1]
    except IndexError:
        print('Error: environment missing\n')
        print('Usage: {} qa|prod'.format(
            sys.argv[0]
        ))
        sys.exit(1)
    if not env.lower() in ('qa', 'prod'):
        print('Error: unknown environment\n')
        print('Usage: {} qa|prod'.format(
            sys.argv[0]
        ))
        sys.exit(1)
    return env


if __name__ == '__main__':
    env = get_env_from_argv(sys.argv)

    configure(env)
    print('** WEBSEARCH MONITOR ENV={} **'.format(env))
    monitor = Monitor(env)

    result = monitor.get_health()
    result = monitor.get_search()
    result = monitor.get_health_celery()

    print('**END**')
