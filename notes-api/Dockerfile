# Start from an official Python image — slim means minimal OS, smaller size
FROM python:3.11-slim

# All commands from here run inside /app inside the container
WORKDIR /app

# Copy requirements first — before the rest of the code.
# WHY: Docker builds in layers, each line is cached.
# If we copy everything at once, changing one line of code
# would force Docker to reinstall all packages from scratch.
# Copying requirements.txt first means packages are only
# reinstalled when dependencies actually change.
COPY requirements.txt .

# Install packages — no-cache-dir keeps the image size small
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]