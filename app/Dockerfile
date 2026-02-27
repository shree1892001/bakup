FROM ubuntu:22.04

# Setup environment
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y \
    cron \
    wget \
    gnupg2 \
    lsb-release \
    rsync \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Add PostgreSQL official repo
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update && apt-get install -y postgresql-client-18 \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirement and install
COPY src/etc/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Copy source code
COPY src/ /app/src/

# Setup logging and permissions
RUN mkdir -p /app/src/log && chmod -R 755 /app/src/log
RUN chmod +x /app/src/services/*.py

# Setup backup directories
RUN mkdir -p /backups/full /backups/incremental

# Setup cron
COPY src/etc/cronjob /etc/cron.d/pg-cron-job
RUN chmod 0644 /etc/cron.d/pg-cron-job
RUN crontab /etc/cron.d/pg-cron-job

CMD ["cron", "-f"]
