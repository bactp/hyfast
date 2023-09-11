# Use an official Python runtime as a parent image
FROM python:3.8

# Install the required packages from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV URL = value1 \
    CLUSTER_NAME = value2

# Copy your Python code into the container
COPY query-cluster-instance.py /app/query-cluster-instance.py

# Compile the Python code into a binary using pyinstaller
RUN pip install pyinstaller && \
    pyinstaller --onefile /app/query-cluster-instance.py && \
    mv /dist/query-cluster-instance /app/query-cluster-instance && \
    rm -rf /app/build /app/__pycache__ /app/query-cluster-instance.spec /app/dist

# Specify the command to run when the container starts
CMD ["/app/query-cluster-instance"]
