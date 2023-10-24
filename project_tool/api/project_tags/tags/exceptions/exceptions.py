from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = 400
    default_detail = "Bad Request."


class AuthenticationFailed(APIException):
    status_code = 401
    default_detail = "Incorrect authentication credentials."
    default_code = "authentication_failed"


class ServerError(APIException):
    status_code = 500
    default_detail = "A server error occurred."
    default_code = "error"


class DatabaseError(APIException):
    status_code = 502
    default_detail = "Database connection error"
    default_code = "error"
