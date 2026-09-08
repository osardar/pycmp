FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
ARG PYCDC_REV=b4289760970dbc399684f1e155ec6d1ea1cc787e
RUN apt-get update && apt-get install -y --no-install-recommends git cmake g++ make \
    && git clone https://github.com/zrax/pycdc.git /opt/pycdc \
    && git -C /opt/pycdc checkout --detach ${PYCDC_REV} \
    && cmake -S /opt/pycdc -B /opt/pycdc/build \
    && cmake --build /opt/pycdc/build -j2 \
    && cp /opt/pycdc/build/pycdc /usr/local/bin/pycdc \
    && pip install --no-cache-dir uncompyle6==3.9.3 xdis==6.1.8 \
    && rm -rf /var/lib/apt/lists/*
LABEL pycmp.pycdc.revision=b4289760970dbc399684f1e155ec6d1ea1cc787e
USER 65534:65534
