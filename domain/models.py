import datetime
import socket
import traceback

import click
import requests

from time_execution.decorator import write_metric

SHORT_HOSTNAME = socket.gethostname()


BASE_URL = dict(
    qa='https://qa.inspirehep.net',
    prod='https://labs.inspirehep.net',
)


class Monitor(object):
    def __init__(self, env):
        self.base_url = BASE_URL[env]

    def _get_request_factory(self, url_path):
        url = '{}/{}'.format(self.base_url, url_path)
        click.echo('GET {}'.format(url))
        try:
            response = requests.get(url, timeout=30)
        except Exception:
            response = None
            traceback.print_exc()
        return response

    def _perform_monitor_for_endpoint(self, name, assertion_func=None):
        response = self._get_request_factory(name)

        try:
            content = response.json()
            if assertion_func:
                assertion_func(content)
        except ValueError:
            click.echo('No JSON response: {}'.format(response.content))
            return
        except Exception:
            click.echo(traceback.format_exc())
            return

        status_code = getattr(response, 'status_code')
        if status_code:
            self._write_metric(http_status_code=status_code, name=name)
            click.echo('Response: {}'.format(status_code))
        return response

    def _write_metric(self, name='default', **kwargs):
        data = dict(
            hostname=SHORT_HOSTNAME,
            origin='inspire-websearch-monitoring',
            name=name,
        )
        data.update(kwargs)
        write_metric(**data)

    def get_health(self):
        """
        $ curl https://labs.inspirehep.net/health
        "Thu, 08 Nov 2018 12:14:19 GMT"
        """
        def assertion(content):
            year = datetime.datetime.today().year
            assert str(year) in content, content

        self._perform_monitor_for_endpoint('health', assertion)

    def get_health_celery(self):
        """
        $ curl https://labs.inspirehep.net/healthcelery
        "Thu, 08 Nov 2018 12:14:44 GMT"
        """
        def assertion(content):
            year = datetime.datetime.today().year
            assert str(year) in content, content

        self._perform_monitor_for_endpoint('healthcelery', assertion)

    def get_search(self):
        """
        $ curl https://labs.inspirehep.net/api/literature/20 | jq
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
        100  1309  100  1309    0     0  21457      0 --:--:-- --:--:-- --:--:-- 21816
        {
          "id": 20,
          "links": {
            "self": "https://labs.inspirehep.net/api/literature/20"
          },
          "metadata": {
            "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
            "control_number": 20,
            "titles": [
              {
                "title": "IRRADIATION OF A CERIUM - CONTAINING SILICATE GLASS"
              }
            ],
            ...
        }
        """
        pid_value = 20
        name = 'api/literature/{}'.format(pid_value)

        def assertion(content):
            assert content['metadata']['control_number'] == pid_value, content

        self._perform_monitor_for_endpoint(name, assertion)
