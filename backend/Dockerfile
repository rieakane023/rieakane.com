FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# psycopg ships self-contained binary wheels, so no libpq build deps are needed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Production default. The dev compose file overrides this with `runserver`.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
