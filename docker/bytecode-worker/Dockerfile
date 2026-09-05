FROM python:3.14-slim
RUN pip install --no-cache-dir xdis uncompyle6
WORKDIR /worker
COPY codegraph/_pyc_worker.py /worker/pyc_worker.py
USER 65534:65534
