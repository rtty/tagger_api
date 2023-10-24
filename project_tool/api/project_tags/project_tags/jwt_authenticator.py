import jwt
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication

from ..tags.exceptions.exceptions import AuthenticationFailed


class Machine(AnonymousUser):
    """Define special User just to make Django REST Framework authentication work"""

    @property
    def is_authenticated(self):
        return True


class M2MAuthentication(authentication.BaseAuthentication):
    """Custom authentication for API m2m authentication"""

    def authenticate(self, request):
        token = (
            request.headers.get("authorization").split()[1]
            if request.headers.get("authorization")
            else None
        )
        if not token:
            raise AuthenticationFailed("Incorrect authentication credentials.")
        decoded = jwt.decode(token, verify=False)
        scopes = decoded["scope"] if "scope" in decoded else None
        if scopes:
            machine = Machine()
            machine.scopes = decoded["scope"].split(" ")
            grand_type = decoded["gty"] if "gty" in decoded else None
            if (
                grand_type == "client-credentials"
                and "userId" not in decoded
                and "roles" not in decoded
            ):
                machine.is_machine = True
                if "azp" not in decoded or decoded["azp"] == "":
                    raise AuthenticationFailed("AZP not provided.")
                else:
                    machine.azp_hash = decoded["azp"]
            return machine, None
        raise AuthenticationFailed("Scope missing from token")
