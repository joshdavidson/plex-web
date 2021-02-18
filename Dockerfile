FROM python:3.9-slim as PREREQS
COPY requirements.txt /
RUN \
pip3 install --upgrade --no-cache-dir pip setuptools && \
pip3 install --no-cache-dir -r /requirements.txt && \
rm /requirements.txt && \
apt clean all && rm -rf /var/cache/apt/*

FROM PREREQS
WORKDIR /opt/plex-web
COPY . /opt/plex-web/
RUN rm -rf venv .idea __pycache__
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages
ENV FLASK_APP=app.py
EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]

