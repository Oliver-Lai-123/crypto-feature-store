FROM apache/airflow:2.8.2

# Use root to copy files into the image
USER root

# Copy requirements into the image. We'll run pip as the non-root `airflow` user
# (the official Airflow image prevents running pip as root).
COPY requirements.txt /tmp/requirements.txt

# Install Python requirements as the `airflow` user so packages are added
# to the user's environment instead of running pip as root.
USER airflow
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Return to root to copy project sources and set ownership
USER root
COPY src /opt/airflow/src
RUN chown -R airflow: /opt/airflow/src

# Switch to the non-root airflow user for runtime
USER airflow

ENV PYTHONPATH=/opt/airflow/src

CMD ["bash", "-c", "airflow webserver"]
