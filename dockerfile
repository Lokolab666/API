FROM python:3.8-slim

# Install essential tools and libraries
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    make \
    libsm6 \
    libxext6 \
    libxrender-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install dlib
RUN pip install dlib

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
