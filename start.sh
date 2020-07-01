#!/bin/bash
memcached -s /tmp/memcached.sock -a 775 -v --memory-limit=8192 --threads=16 > /tmp/memcached.log &
uwsgi --ini /app/uwsgi.ini