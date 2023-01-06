FROM python:3

# Create a working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the source code
COPY . .

# Run the application
CMD ["python","-m","bot"]
