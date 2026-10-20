FROM python:3.11.2-slim-bullseye@sha256:2f749ef90f54fd4b3c77cde78eec23ab5b8199d9ac84e4ced6ae523ef223ef7b

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
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
       libxkbcommon0 \
       libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --requirement requirements.lock

COPY app ./app
COPY assets ./assets
COPY demo ./demo
COPY tests ./tests
# The image is a finite, offscreen smoke-test environment. Start the GUI
# explicitly on a native desktop; see README.md for the supported commands.
CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
