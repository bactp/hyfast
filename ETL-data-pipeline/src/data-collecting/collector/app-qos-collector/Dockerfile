# Use an official Python runtime as a parent image
FROM python:3.8

# Install the required packages from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV URL = value1 \
    CLUSTER_NAME = value2 \
    NAME_SPACE = value3 \
    DEST_WORKLOAD = value4

# Copy your Python code into the container
COPY query-app-qos.py /app/query-app-qos.py

# Compile the Python code into a binary using pyinstaller
RUN pip install pyinstaller && \
    pyinstaller --onefile /app/query-app-qos.py && \
    mv /dist/query-app-qos /app/query-app-qos && \
    rm -rf /app/build /app/__pycache__ /app/query-app-qos.spec /app/dist

# Specify the command to run when the container starts
CMD ["/app/query-app-qos"]