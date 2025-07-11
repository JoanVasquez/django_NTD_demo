# 🌐 centralized_error_handler.py - Centralized error handling middleware
# for Django with OTEL tracing, structured JSON logging,
# and support for BaseAppException structured business errors.

import logging
import traceback

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from opentelemetry import trace

from utils.exceptions import BaseAppException

# 🪵 Logger and tracer initialization
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class CentralizedErrorHandlerMiddleware(MiddlewareMixin):
    """
    🛡️ Centralized error handler with structured logging, OTEL tracing,
    and support for BaseAppException structured business errors.
    """

    def process_exception(self, request, exception):
        """
        ⚠️ Processes exceptions globally, returning JSON responses for
        known business errors or a generic 500 for unhandled errors.
        """
        path = request.path
        method = request.method

        with tracer.start_as_current_span("exception_handler") as span:
            span.set_attribute("http.path", path)
            span.set_attribute("http.method", method)

            if isinstance(exception, BaseAppException):
                # 🚩 Handle predictable business (known) exceptions
                span.set_attribute("exception.type", "BaseAppException")
                span.set_attribute("exception.message", exception.message)

                logger.warning(
                    "⚠️ Business exception occurred",
                    extra={
                        "path": path,
                        "method": method,
                        "error_message": exception.message,
                        "payload": exception.payload,
                        "status_code": exception.status_code,
                    },
                )
                return JsonResponse(
                    exception.to_dict(),
                    status=exception.status_code,
                )

            # ❌ Handle unhandled, unknown exceptions gracefully
            error_message = str(exception)
            stack_trace = traceback.format_exc()

            span.record_exception(exception)
            span.set_attribute("exception.type", type(exception).__name__)
            span.set_attribute("exception.message", error_message)

            logger.error(
                "❌ Unhandled exception occurred",
                extra={
                    "path": path,
                    "method": method,
                    "error_message": error_message,
                    "stack_trace": stack_trace,
                },
            )
            response = {
                "status": "error",
                "message": (
                    "An internal server error occurred. " "Please contact support."
                ),
            }
            return JsonResponse(response, status=500)
