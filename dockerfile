# Use the official Apache Airflow image as the base image
FROM apache/airflow:2.10.1
ARG AIRFLOW_VERSION=2.10.1
USER root
RUN groupadd -g 1000 airflow || true && \
    useradd -m -u 50000 -g airflow airflow || true && \
    mkdir -p /opt/airflow/logs/scheduler && \
    chown -R airflow:airflow /opt/airflow && \
    chmod -R 755 /opt/airflow/logs

RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


USER airflow
COPY requirements.txt /

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
