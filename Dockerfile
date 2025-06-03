FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY ./req.txt .

# Install dependencies
RUN pip install --no-cache-dir -r req.txt

# Expose the app's port
EXPOSE 5002

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Command to run the app
CMD ["python", "app.py", "--host=0.0.0.0", "--port=5002"]
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5002", "--debug"]
