FROM python:3.6
RUN useradd -ms /bin/bash admin
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN pip install uwsgi
RUN pip install -r requirements.txt

USER admin

EXPOSE 5000/tcp
ENV PYTHONPATH /app
CMD ["uwsgi","--socket","0.0.0.0:80", "source/wsgi:app"]