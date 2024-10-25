# Use the official Apache Airflow image as the base image
FROM apache/airflow:2.10.1

COPY requirements.txt /

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
