#!/bin/bash
memcached -d logfile /var/log/memcached.log -s /app/memcached.sock -a 775 -v --memory-limit=8192 --threads=16
uwsgi --ini /app/uwsgi.ini