FROM python:3.6
RUN useradd -ms /bin/bash admin
RUN mkdir -p /app

WORKDIR /app
RUN pip install --upgrade pip \
 && pip install uwsgi\
 && apt-get update\
 && apt-get install -y memcached libmemcached-dev



COPY . /app
COPY ./start.sh /app/source/start.sh
RUN pip install -r /app/requirements.txt && chmod +x /app/source/start.sh
USER admin


EXPOSE 5000/tcp
ENV PYTHONPATH /app
ENV MEMCACHED_URL /app/memcached.sock:0
WORKDIR /app/source
#CMD ["python","-m","flask","run","--host=0.0.0.0"]
#CMD ["uwsgi","--","0.0.0.0:5000","--protocol","http","-w","source.wsgi:app", "-M","--workers","6","--wsgi-disable-file-wrapper", "--enable-threads"]
CMD ["./start.sh"]
