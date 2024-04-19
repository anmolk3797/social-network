from datetime import datetime
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from social_network.settings import SIMPLE_JWT
from http import HTTPStatus
from rest_framework.response import Response

def normalize_email(email: str) -> str:
    """
    Normalize the given email address.

    This function takes an email address as input and performs normalization by stripping leading and trailing whitespace
    and converting the email address to lowercase.

    Args:
        email (str): The email address to normalize.

    Returns:
        str: The normalized email address.
    """
    return email.strip().lower()

class AuthService:
    def __tokens_for_user(self, user: CustomUser) -> dict:
        """generate tokens"""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {
            "refresh": str(refresh),
            "access": access_token,
        }

    def get_auth_tokens_for_user(self, user: CustomUser) -> dict:
        """call private method to generate refresh and access token"""
        return self.__tokens_for_user(user)


def get_non_fields_errors(error) -> dict:
    """set non field errors"""
    return {"non_field_errors": [error]}


class AppResponse:
    """
    class App Response that return Json Response
    """

    @staticmethod
    def response(status_code: HTTPStatus, messages: list, **kwargs) -> Response:
        """static method that return Json Response
        :param: status_code (status code of Http Request)
        :param: message (string of success or error message)
        """
        messages = messages if isinstance(messages, list) else [messages]
        response_dict = {"messages": messages}
        response_dict.update(**kwargs)
        return Response(response_dict, status=status_code)

    def success(self, status_code=HTTPStatus.OK, messages=None, **kwargs):
        """function that return status code and message to response
        :param: status_code (status code of Http Request)
        :param: message (message string)
        """
        return self.response(status_code, messages or ["Success"], **kwargs)

    def error(self, status_code=HTTPStatus.BAD_REQUEST, messages=None, **kwargs):
        """function that return status code and message to response
        :param: status_code (status code of Http Request)
        :param: message (message string)
        """
        if not isinstance(messages, list):
            messages = [get_non_fields_errors(messages)]
        return self.response(
            status_code,
            messages=messages or [get_non_fields_errors("Exception Occurred")],
            **kwargs,
        )

    def json_data(self, status_code=HTTPStatus.OK, messages=None, **kwargs):
        """function that return status code and message to response
        :param: status_code (status code of Http Request)
        :param: message (message string)
        :param: kwargs (dict)
        :Returns: JsonResponse
        """
        return self.response(status_code, messages, **kwargs)

    def deleted(self, status_code=HTTPStatus.NO_CONTENT, messages=None, **kwargs):
        """function that return status code and message to response
        :param: status_code (status code of Http Request)
        :param: message (message string)
        :param: kwargs (dict)
        :Returns: JsonResponse
        """
        return self.response(status_code, messages or ["Deleted"], **kwargs)