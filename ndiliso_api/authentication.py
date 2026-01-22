from rest_framework.exceptions import AuthenticationFailed
import jwt
from .models import User

def authenticate_request(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        raise AuthenticationFailed('Authorization header missing')

    try:
        prefix, token = auth_header.split(' ')
        if prefix.lower() != 'bearer':
            raise AuthenticationFailed('Invalid token prefix')
    except ValueError:
        raise AuthenticationFailed('Invalid Authorization header format')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')

    user = User.objects.filter(id=payload['id']).first()
    if user is None:
        raise AuthenticationFailed('User not found')

    return user