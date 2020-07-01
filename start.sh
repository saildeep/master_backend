#!/bin/bash
memcached -d --port=11211 -udp-port=11211 --listen=0.0.0.0 -v --memory-limit=8192 --threads=16
uwsgi --ini /app/uwsgi.ini