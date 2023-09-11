# Use an official Python runtime as a parent image
FROM python:3.8

# Install the required packages from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV URL = value1

# Copy your Python code into the container
COPY query-compute-host.py /app/query-compute-host.py

# Compile the Python code into a binary using pyinstaller
RUN pip install pyinstaller && \
    pyinstaller --onefile /app/query-compute-host.py && \
    mv /dist/query-compute-host /app/query-compute-host && \
    rm -rf /app/build /app/__pycache__ /app/query-compute-host.spec /app/dist

# Specify the command to run when the container starts
CMD ["/app/query-compute-host"]
