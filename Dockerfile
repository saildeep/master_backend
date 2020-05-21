FROM python:3.6
RUN useradd -ms /bin/bash admin
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install uwsgi
RUN pip install -r requirements.txt

USER admin

EXPOSE 5000/tcp
ENV PYTHONPATH /app
WORKDIR /app/source
#CMD ["python","-m","flask","run","--host=0.0.0.0"]
#CMD ["uwsgi","--","0.0.0.0:5000","--protocol","http","-w","source.wsgi:app", "-M","--workers","6","--wsgi-disable-file-wrapper", "--enable-threads"]
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
