"""Minimal Google OAuth 2.0 (sign in with Google) using only the stdlib.

Credentials come from the GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET secrets.
When they are not configured, ``google_configured()`` is False and the
login screen hides the Google button.
"""
import base64
import json
import secrets
import urllib.parse
import urllib.request

AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
TOKENINFO_ENDPOINT = 'https://oauth2.googleapis.com/tokeninfo'
SCOPE = 'openid email profile'


def _setting(name):
    from django.conf import settings

    return getattr(settings, name, '') or ''


def google_configured():
    return bool(_setting('GOOGLE_CLIENT_ID') and _setting('GOOGLE_CLIENT_SECRET'))


def redirect_uri(request):
    """Public callback URL — never hardcodes a host (sandbox-safe)."""
    from django.conf import settings

    public_host = getattr(settings, 'BASE44_PUBLIC_HOST_SUFFIX', '')
    if public_host and request.get_host().endswith(public_host):
        # Behind the preview proxy: build the URL from the public origin.
        origin = request.headers.get('Origin') or request.build_absolute_uri('/').rstrip('/')
        return urllib.parse.urljoin(origin, '/accounts/google/callback/')
    return request.build_absolute_uri('/accounts/google/callback/')


def build_authorization_url(request):
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    params = {
        'client_id': _setting('GOOGLE_CLIENT_ID'),
        'redirect_uri': redirect_uri(request),
        'response_type': 'code',
        'scope': SCOPE,
        'state': state,
        'prompt': 'select_account',
    }
    return AUTH_ENDPOINT + '?' + urllib.parse.urlencode(params)


def exchange_code(request, code):
    data = urllib.parse.urlencode({
        'code': code,
        'client_id': _setting('GOOGLE_CLIENT_ID'),
        'client_secret': _setting('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': redirect_uri(request),
        'grant_type': 'authorization_code',
    }).encode()
    req = urllib.request.Request(
        TOKEN_ENDPOINT, data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read())
    return validate_id_token(payload.get('id_token', ''))


def validate_id_token(id_token):
    """Validate the token via Google's tokeninfo endpoint (server-side check)."""
    if not id_token:
        raise ValueError('id_token ausente')
    url = TOKENINFO_ENDPOINT + '?' + urllib.parse.urlencode({'id_token': id_token})
    with urllib.request.urlopen(url, timeout=15) as resp:
        info = json.loads(resp.read())
    if info.get('aud') != _setting('GOOGLE_CLIENT_ID'):
        raise ValueError('token de audiência inválida')
    if info.get('email_verified') in (False, 'false'):
        raise ValueError('e-mail não verificado')
    return {
        'email': info.get('email'),
        'given_name': info.get('given_name', ''),
        'family_name': info.get('family_name', ''),
        'picture': info.get('picture', ''),
    }
