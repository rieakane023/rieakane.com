"""Fast, isolated settings for the test suite (django.md §17)."""
from .settings import *  # noqa: F401,F403

# In-memory SQLite — fast and disposable.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Fast password hashing for tests only.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Exercise the non-MFA login paths by default; MFA-required behaviour is tested
# explicitly via the `settings` fixture.
REQUIRE_MFA = False

# Don't let throttling interfere with the test suite.
REST_FRAMEWORK = {**REST_FRAMEWORK}  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": None, "user": None, "login": None}
