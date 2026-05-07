"""测试 app/core/exceptions.py"""

import pytest

from app.core.exceptions import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


class TestAppException:
    def test_base_exception_defaults(self):
        exc = AppException()
        assert exc.status_code == 500
        assert exc.error_code == "INTERNAL_ERROR"
        assert str(exc) == ""

    def test_base_exception_custom(self):
        exc = AppException(detail="custom error", status_code=400, error_code="CUSTOM")
        assert exc.status_code == 400
        assert exc.error_code == "CUSTOM"
        assert exc.detail == "custom error"
        assert str(exc) == "custom error"

    def test_not_found_exception(self):
        exc = NotFoundException()
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND"

    def test_not_found_exception_custom_detail(self):
        exc = NotFoundException(detail="User not found")
        assert exc.detail == "User not found"

    def test_validation_exception(self):
        exc = ValidationException()
        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"

    def test_unauthorized_exception(self):
        exc = UnauthorizedException()
        assert exc.status_code == 401
        assert exc.error_code == "UNAUTHORIZED"

    def test_forbidden_exception(self):
        exc = ForbiddenException()
        assert exc.status_code == 403
        assert exc.error_code == "FORBIDDEN"

    def test_conflict_exception(self):
        exc = ConflictException()
        assert exc.status_code == 409
        assert exc.error_code == "CONFLICT"

    def test_all_exceptions_are_app_exceptions(self):
        for exc_cls in [
            NotFoundException,
            ValidationException,
            UnauthorizedException,
            ForbiddenException,
            ConflictException,
        ]:
            assert issubclass(exc_cls, AppException)
