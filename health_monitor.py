import os
import sys
import warnings

import click
import time_execution

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


@click.group()
def cli():
    pass


@click.command()
def prod():
    perform_monitoring('prod')


@click.command()
def qa():
    perform_monitoring('qa')


cli.add_command(prod)
cli.add_command(qa)


def perform_monitoring(env):
    configure(env)
    monitor = Monitor(env)
    monitor.get_health()
    monitor.get_search()
    monitor.get_health_celery()


if __name__ == '__main__':
    print('** INSPIRE HEALTH MONITOR **')
    cli()
