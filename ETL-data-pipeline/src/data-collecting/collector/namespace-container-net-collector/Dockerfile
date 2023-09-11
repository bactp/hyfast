# Use an official Python runtime as a parent image
FROM python:3.8

# Install the required packages from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV URL = value1 \
    CLUSTER_NAME = value2 \
    NAME_SPACE = value3

# Copy your Python code into the container
COPY query-namespace-container-network.py /app/query-namespace-container-network.py

# Compile the Python code into a binary using pyinstaller
RUN pip install pyinstaller && \
    pyinstaller --onefile /app/query-namespace-container-network.py && \
    mv /dist/query-namespace-container-network /app/query-namespace-container-network && \
    rm -rf /app/build /app/__pycache__ /app/query-namespace-container-network.spec /app/dist

# Specify the command to run when the container starts
CMD ["/app/query-namespace-container-network"]