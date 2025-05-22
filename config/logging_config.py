import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from django.conf import settings
from pathlib import Path
import logging.config

LOG_DIR = Path(settings.BASE_DIR) / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {module} {funcName} {lineno} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s %(pathname)s',
        },
        'request_formatter': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s %(pathname)s %(lineno)d %(request_method)s %(request_url)s %(status_code)d %(remote_addr)s %(user_agent)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': getattr(settings, 'LOG_MAX_BYTES', 1024 * 1024 * 15),  # 15MB
            'backupCount': getattr(settings, 'LOG_BACKUP_COUNT', 10),
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': getattr(settings, 'LOG_MAX_BYTES', 1024 * 1024 * 15),  # 15MB
            'backupCount': getattr(settings, 'LOG_BACKUP_COUNT', 5),
            'formatter': 'json',
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'debug.log'),
            'maxBytes': getattr(settings, 'LOG_MAX_BYTES', 1024 * 1024 * 15),  # 15MB
            'backupCount': getattr(settings, 'LOG_BACKUP_COUNT', 5),
            'formatter': 'verbose',
        },
        'request_info_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'info.log'),
            'maxBytes': getattr(settings, 'LOG_MAX_BYTES', 1024 * 1024 * 15),  # 15MB
            'backupCount': getattr(settings, 'LOG_BACKUP_COUNT', 10),
            'formatter': 'request_formatter',
        },
        'request_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': getattr(settings, 'LOG_MAX_BYTES', 1024 * 1024 * 15),  # 15MB
            'backupCount': getattr(settings, 'LOG_BACKUP_COUNT', 10),
            'formatter': 'request_formatter',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'debug_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'project.requests.info': {
            'handlers': ['request_info_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'project.requests.error': {
            'handlers': ['request_error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


class RequestLoggingMiddleware:
    """Middleware to log HTTP requests in JSON format."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.info_logger = logging.getLogger('project.requests.info')
        self.error_logger = logging.getLogger('project.requests.error')

    def __call__(self, request):
        response = self.get_response(request)

        # Prepare log data
        try:
            log_data = {
                'request_method': request.method,
                'request_url': request.get_full_path(),
                'status_code': response.status_code,
                'remote_addr': request.META.get('REMOTE_ADDR', 'unknown'),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
                'message': f'HTTP {request.method} request to {request.get_full_path()}',
            }
        except Exception as e:
            log_data = {
                'request_method': 'unknown',
                'request_url': 'unknown',
                'status_code': getattr(response, 'status_code', 500),
                'remote_addr': 'unknown',
                'user_agent': 'unknown',
                'message': f'Error preparing log data: {str(e)}',
            }

        # Custom error messages
        if log_data['status_code'] == 404:
            log_data['message'] = f'Not Found: {log_data["request_url"]}'
        elif log_data['status_code'] == 401:
            log_data['message'] = f'Unauthorized: {log_data["request_url"]}'

        # Log based on status code
        if log_data['status_code'] >= 400:
            self.error_logger.error(log_data)
        else:
            self.info_logger.info(log_data)

        return response


def get_custom_logger(name):
    """
    Create a custom logger for a specific module with JSON output.

    Args:
        name (str): Name of the logger (e.g., 'myapp.module').

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    custom_handler = RotatingFileHandler(
        filename=str(LOG_DIR / f'{name}.log'),
        maxBytes=getattr(settings, 'LOG_MAX_BYTES', 1024 * 1024 * 15),  # 15MB
        backupCount=getattr(settings, 'LOG_BACKUP_COUNT', 10)
    )
    custom_handler.setFormatter(jsonlogger.JsonFormatter())

    if not logger.handlers:
        logger.addHandler(custom_handler)

    return logger


# Apply logging configuration
logging.config.dictConfig(LOGGING)