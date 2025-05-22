# Django Request Logger

A robust and customizable logging system for Django applications, designed to log HTTP requests in structured JSON format. This package separates successful (status codes < 400) and failed (status codes >= 400) requests into distinct log files (`info.log` and `errors.log`), facilitating efficient monitoring and analysis of application behavior.

## 🚀 Features

- **Comprehensive Request Logging**: Captures method, path, status code, client IP, and User-Agent for every request.
- **Structured JSON Logs**: Easily parse and analyze with tools like Kibana or Graylog.
- **Log Separation by Status Code**:
  - ✅ `logs/info.log`: Logs successful requests (status < 400).
  - ❌ `logs/errors.log`: Logs failed requests (status >= 400).
- **Custom Error Messages**:
  - 404 → "Not Found"
  - 401 → "Unauthorized"
- **Log Rotation**:
  - Max file size: 15MB
  - Backups: 10 for info, 5 for error
- **Lightweight**: File-based logging with no email alerts.

---

## 📦 Installation

1. **Install required package**:

   ```bash
   pip install python-json-logger

2. **Integrate with Django Project**:
   - Copy the `logging_config.py` file to your Django project directory (e.g., `your_project/config/`).
   - Update your Django `settings.py` to include the logging configuration:

     ```python
     from pathlib import Path
     from .config.logging_config import LOGGING

     BASE_DIR = Path(__file__).resolve().parent.parent
     ```

   - Add the `RequestLoggingMiddleware` to the `MIDDLEWARE` setting in `settings.py`:

     ```python
     MIDDLEWARE = [
         # ... other middleware
         'your_project.config.logging_config.RequestLoggingMiddleware',
     ]
     ```

## Usage

The `RequestLoggingMiddleware` automatically logs all HTTP requests to your Django application:

- **Successful Requests** (status codes < 400, e.g., 200, 201) are logged in `logs/info.log`.
- **Failed Requests** (status codes >= 400, e.g., 401, 404, 500) are logged in `logs/errors.log`.

### Example Log Entries

**`info.log` Example** (Successful Request):

```json
{
    "levelname": "INFO",
    "asctime": "2025-04-30 06:52:09,533",
    "name": "project.requests.info",
    "message": "HTTP GET request to /api/v1/bmc/communication-channel/",
    "pathname": "...",
    "lineno": 128,
    "request_method": "GET",
    "request_url": "/api/v1/bmc/communication-channel/",
    "status_code": 200,
    "remote_addr": "127.0.0.1",
    "user_agent": "PostmanRuntime/7.43.3"
}
```

**`errors.log` Example** (Failed Request):

```json
{
    "levelname": "ERROR",
    "asctime": "2025-04-30 06:52:13,823",
    "name": "project.requests.error",
    "message": "Unauthorized: /api/v1/bmc/communication-channel/",
    "pathname": "...",
    "lineno": 126,
    "request_method": "GET",
    "request_url": "/api/v1/bmc/communication-channel/",
    "status_code": 401,
    "remote_addr": "127.0.0.1",
    "user_agent": "PostmanRuntime/7.43.3"
}
```

## Directory Structure

Ensure your project directory includes a `logs/` folder to store the log files. The middleware will create `info.log` and `errors.log` automatically. A suggested structure is:

```
your_project/
├── config/
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── settings.py
│   └── logging_config.py
├── logs/
│   ├── info.log
│   └── errors.log
├── app_name
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serilizers.py
│   ├── views.py
│   └── urls.py
└── ...
```

## Notes

- Ensure the `logs/` directory has appropriate write permissions for the application to create and write to log files.
- The logging configuration is optimized for JSON output, making it compatible with log aggregation tools.
- For custom loggers, refer to `logging_config.py` to extend logging for specific application modules.

## Contributing

Contributions are welcome! Please submit issues or pull requests to the [GitHub repository](https://github.com/your-username/django-request-logger). Ensure any changes include tests and adhere to the project's coding standards.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.