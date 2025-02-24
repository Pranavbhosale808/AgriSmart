import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crop_recommendation_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Automatically use the host and port from .env
    host = os.getenv("DJANGO_RUN_HOST", "127.0.0.1")
    port = os.getenv("DJANGO_PORT", "8000")

    # Only override command when no argument is provided
    if len(sys.argv) == 1:
        sys.argv = ["manage.py", "runserver", f"{host}:{port}"]

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
