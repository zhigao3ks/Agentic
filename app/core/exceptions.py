"""项目统一异常类。"""


class AppException(Exception):
    """应用异常基类。"""

    def __init__(self, detail: str = "", status_code: int = 500, error_code: str = "INTERNAL_ERROR") -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class NotFoundException(AppException):
    """资源未找到。"""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404, error_code="NOT_FOUND")


class ValidationException(AppException):
    """请求参数校验失败。"""

    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(detail=detail, status_code=422, error_code="VALIDATION_ERROR")


class UnauthorizedException(AppException):
    """未认证。"""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(detail=detail, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenException(AppException):
    """无权限。"""

    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(detail=detail, status_code=403, error_code="FORBIDDEN")


class ConflictException(AppException):
    """资源冲突（如重复创建）。"""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(detail=detail, status_code=409, error_code="CONFLICT")
