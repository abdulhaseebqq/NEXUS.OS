class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: str,
        details=None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

        super().__init__(message)


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="User not found",
            status_code=404,
            error_code="USER_NOT_FOUND",
        )


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            status_code=401,
            error_code="INVALID_CREDENTIALS",
        )


class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(
            message="Permission denied",
            status_code=403,
            error_code="PERMISSION_DENIED",
        )


class SessionNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Session not found",
            status_code=404,
            error_code="SESSION_NOT_FOUND",
        )


class ResourceConflictError(AppException):
    def __init__(
        self,
        message: str,
        error_code: str = "RESOURCE_CONFLICT",
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
        )
