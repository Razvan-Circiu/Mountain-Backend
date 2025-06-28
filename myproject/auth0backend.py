import json
import requests
from jose import jwt
from rest_framework import authentication, exceptions

class Auth0JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Obține tokenul JWT din header-ul Authorization
        auth = request.headers.get('Authorization', None)
        if not auth:
            raise exceptions.AuthenticationFailed('Authorization header missing')

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Authorization header must start with Bearer')
        elif len(parts) == 1:
            raise exceptions.AuthenticationFailed('Token missing')
        elif len(parts) > 2:
            raise exceptions.AuthenticationFailed('Authorization header must be Bearer token')

        token = parts[1]

        # Verifică dacă tokenul este valid
        try:
            payload = self.decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('token is expired')
        except jwt.JWTClaimsError:
            raise exceptions.AuthenticationFailed('Incorrect claims, please check the audience and issuer')
        except Exception:
            raise exceptions.AuthenticationFailed('Unable to parse authentication token.')

        return (payload, token)

    def decode_jwt(self, token):
        # Verifică semnătura tokenului JWT folosind cheia publică de la Auth0
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise exceptions.AuthenticationFailed('Invalid header string: must contain a valid JWT')

        rsa_key = {}
        if 'kid' in unverified_header:
            try:
                rsa_key = self.get_rsa_key(unverified_header['kid'])
            except requests.exceptions.RequestException as e:
                raise exceptions.AuthenticationFailed('Failed to retrieve RSA key')

        payload = jwt.decode(token, rsa_key, algorithms=["RS256"], audience=AUTH0_CLIENT_ID)
        return payload

    def get_rsa_key(self, kid):
        # Fetch the public key from Auth0 for verification
        try:
            url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
            response = requests.get(url)
            response.raise_for_status()
            jwks = response.json()

            # Look for the correct key by matching the kid
            for key in jwks['keys']:
                if key['kid'] == kid:
                    return {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e'],
                    }
            raise exceptions.AuthenticationFailed('Unable to find appropriate key')

        except requests.exceptions.RequestException as e:
            raise exceptions.AuthenticationFailed(f'Unable to fetch RSA keys from Auth0: {str(e)}')
