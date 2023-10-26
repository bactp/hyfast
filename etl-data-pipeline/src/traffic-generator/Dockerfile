# Use an official Python runtime as a parent image
FROM python:3.8

# Install the required packages from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV CLUSTER_NAME = value1 \
    NAME_SPACE = value2 \
    TARGET_HOST = value3

# Copy your Python code into the container
COPY locustfile.py /app/locustfile.py
COPY traffic_pattern_gen.py /app/traffic_pattern_gen.py
COPY load_gen.sh /app/load_gen.sh

# Compile the Python code into a binary using pyinstaller
RUN pip install pyinstaller && \
    pyinstaller --onefile /app/locustfile.py && \
    pyinstaller --onefile /app/traffic_pattern_gen.py && \
    mv /dist/locustfile /app/locustfile && \
    mv /dist/traffic_pattern_gen /app/traffic_pattern_gen && \
    rm -rf /app/build /app/__pycache__ /app/locustfile.spec /app/dist && \
    rm -rf /app/build /app/__pycache__ /app/traffic_pattern_gen.spec /app/dist

RUN chmod +x /app/load_gen.sh
# Specify the command to run when the container starts
CMD ["/app/load_gen.sh"]
