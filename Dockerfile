# Python image base
FROM python:3.10-slim

# Establish the working directory in /app
WORKDIR /app

# Copy the file requirements.txt and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the files of the project
COPY . .

# Expose the port 8000 to access to the server
EXPOSE 8000

# Command to execute the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]