def api_client_with_credentials(token, api_client):
    return api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
