FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    cron \
    wget \
    gnupg2 \
    lsb-release \
    rsync \
    python3 \
    python3-pip

# Add PostgreSQL official repo
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update && apt-get install -y postgresql-client-18

COPY scripts/ /scripts/
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN chmod +x /scripts/*.py /scripts/*.sh

RUN mkdir -p /backups/full
RUN mkdir -p /backups/incremental

COPY restore.py /restore.py
COPY cronjob /etc/cron.d/pg-cron-job
RUN chmod 0644 /etc/cron.d/pg-cron-job
RUN crontab /etc/cron.d/pg-cron-job

CMD ["cron", "-f"]