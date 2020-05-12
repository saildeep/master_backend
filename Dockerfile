FROM python:3.6
RUN pwd
RUN ls
RUN pip install -r requirements.txt
RUN useradd -ms /bin/bash admin
USER admin
WORKDIR /source
COPY source /source
CMD ["python", "webserver.py"]
EXPOSE 5000/tcp