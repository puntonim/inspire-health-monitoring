# Inspire Health Monitoring

Usage:
```bash
$ pip install -r requirements/requirements-base.txt
$ APPMETRICS_ELASTICSEARCH_USERNAME=myuser APPMETRICS_ELASTICSEARCH_PASSWORD=mypass python health_monitor.py qa
# Or with the Makefile:
$ make venv
$ APPMETRICS_ELASTICSEARCH_USERNAME=myuser APPMETRICS_ELASTICSEARCH_PASSWORD=mypass make qa
```
