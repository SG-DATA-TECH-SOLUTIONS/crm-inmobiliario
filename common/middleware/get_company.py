import logging

import jwt
from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed

from common.models import Org, Profile

logger = logging.getLogger(__name__)


class GetProfileAndOrg(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        request.profile = None
        user_id = None

        try:
            if request.headers.get("Authorization"):
                token1 = request.headers.get("Authorization")
                token = token1.split(" ")[1]
                decoded = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO]
                )
                user_id = decoded["user_id"]
        except jwt.ExpiredSignatureError:
            return
        except jwt.InvalidTokenError:
            return
        except (IndexError, KeyError):
            return

        api_key = request.headers.get("Token")
        if api_key:
            try:
                organization = Org.objects.get(api_key=api_key)
                request.META["org"] = organization.id
                profile = Profile.objects.filter(
                    org=organization, role="ADMIN"
                ).first()
                if profile:
                    user_id = profile.user.id
            except Org.DoesNotExist:
                raise AuthenticationFailed("Invalid API Key")

        if user_id is not None and request.headers.get("org"):
            try:
                profile = Profile.objects.get(
                    user_id=user_id,
                    org=request.headers.get("org"),
                    is_active=True,
                )
                request.profile = profile
            except Profile.DoesNotExist:
                logger.warning(
                    "Profile not found for user %s in org %s",
                    user_id,
                    request.headers.get("org"),
                )
