import jwt
from flask import request, jsonify, g

from AssetManagement.src.app.utils.utils import Utils

def auth_middleware():
    if request.path in ['/login', '/signup']:
        return None

    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized, missing or invalid token'}), 401

    token = auth_token.split(' ')[1]
    try:
        # Decode the token using the secret key
        decoded_token = Utils.decode_jwt_token(token)

        # Extract user_id and role from the decoded token
        user_id = decoded_token.get("user_id")
        role = decoded_token.get("role")

        if not user_id or not role:
            return jsonify({'error': 'Unauthorized, invalid token payload'}), 401

        # Set user_id and role in Flask's global context
        g.user_id = user_id
        g.role = role

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Unauthorized, token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Unauthorized, invalid token'}), 401