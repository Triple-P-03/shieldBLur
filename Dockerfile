FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QT_QPA_PLATFORM=offscreen

WORKDIR /opt/shieldblur

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libdbus-1-3 \
       libegl1 \
       libfontconfig1 \
       libgl1 \
       libglib2.0-0 \
       libx11-xcb1 \
       libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.lock ./
RUN python -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY app ./app
COPY assets ./assets
COPY demo ./demo
COPY tests ./tests
COPY Makefile README.md .python-version ./

CMD ["python", "-m", "app"]
