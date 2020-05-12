FROM python:3.6
RUN useradd -ms /bin/bash admin
RUN mkdir -p /app
ADD ./* /app/

WORKDIR /app
RUN pip install -r requirements.txt

USER admin

EXPOSE 5000/tcp

CMD ["python", "source/webserver.py"]