FROM python:3.6
RUN useradd -ms /bin/bash admin
COPY source /source

WORKDIR /source
RUN pip install -r requirements.txt

USER admin

EXPOSE 5000/tcp

CMD ["python", "webserver.py"]