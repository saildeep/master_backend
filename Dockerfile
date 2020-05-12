FROM tiangolo/uwsgi-nginx-flask:python3.8
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

USER admin

EXPOSE 5000/tcp
ENV PYTHONPATH /app
CMD ["python", "source/webserver.py"]