FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY ./req.txt .

# Install dependencies
RUN pip install --no-cache-dir -r req.txt

# Expose the app's port
EXPOSE 5002

# Command to run the app
CMD ["python", "app.py", "--host=0.0.0.0", "--port=5002"]
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--certfile=/etc/ssl/certs/apache2.crt", "--keyfile=/etc/ssl/private/apache2.key", "app:app"]
