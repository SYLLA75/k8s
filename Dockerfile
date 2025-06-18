FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
COPY ui ./ui
COPY ansible ./ansible
COPY database ./database
RUN mkdir /data
VOLUME ["/data"]
ENV FLASK_APP=ui/app.py
CMD ["flask", "run", "--host", "0.0.0.0"]
