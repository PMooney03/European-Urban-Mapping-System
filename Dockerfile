FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create staticfiles directory and collect static files
RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD gunicorn european_mapping.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2




