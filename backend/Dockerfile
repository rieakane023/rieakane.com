FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# psycopg ships self-contained binary wheels, so no libpq build deps are needed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake static files into the image (WhiteNoise serves them). Safe at build time:
# collectstatic doesn't touch the database.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Production default. Runs migrations at startup (Render free tier has no
# pre-deploy command), then binds the platform-provided $PORT (Render/Cloud Run),
# falling back to 8000 locally. `sh -c … exec` lets $PORT expand while gunicorn
# still becomes PID 1 and receives OS signals (clean shutdown). The dev compose
# file overrides this with its own `migrate && runserver`.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
