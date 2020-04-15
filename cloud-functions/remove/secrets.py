from os import environ
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

def get_secret (secret_id):
    name = client.secret_version_path(environ["GCP_PROJECT"], secret_id, "latest")
    response = client.access_secret_version(name)
    return response.payload.data.decode('UTF-8')