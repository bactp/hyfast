# Use an official Python runtime as a parent image
FROM python:3.8

# Set environment variables
ENV URL = value1 \
    CLUSTER_NAME = value2

# Copy your Python code into the container
COPY query-cluster.py /query-cluster.py

#Install Python dependencies using pip
RUN pip install requests minio

# Specify the command to run when the container starts
CMD ["python", "/query-cluster.py"]
