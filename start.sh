#!/bin/bash
memcached -s /app/memcached.sock -a 775 -v --memory-limit=8192 --threads=16 > /app/memcached.log &
uwsgi --ini /app/uwsgi.ini