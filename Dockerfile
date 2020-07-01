FROM python:3.6
RUN useradd -ms /bin/bash admin
RUN mkdir -p /app

WORKDIR /app
RUN pip install --upgrade pip \
 && pip install uwsgi\
 && apt-get update\
 && apt-get install -y memcached\
 &&  sed -i 's/-m 64/-m 4000/g' /etc/memcached.conf

USER admin

COPY . /app
COPY ./start.sh /app/source/start.sh
RUN pip install -r requirements. && chmod +x /app/source/start.sh



EXPOSE 5000/tcp
ENV PYTHONPATH /app
WORKDIR /app/source
#CMD ["python","-m","flask","run","--host=0.0.0.0"]
#CMD ["uwsgi","--","0.0.0.0:5000","--protocol","http","-w","source.wsgi:app", "-M","--workers","6","--wsgi-disable-file-wrapper", "--enable-threads"]
CMD ["./start.sh"]
