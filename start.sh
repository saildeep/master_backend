#!/bin/bash
memcached -d
uwsgi --ini /app/uwsgi.ini