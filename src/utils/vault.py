import os

import hvac
from hvac.exceptions import VaultError

from src.utils.parser import parse_config


def get_secrets(connection):
    """
    Get secrets from Vault.

    Parameters
    ----------
    connection: str
        The application/connection to get secrets for.

    Returns
    -------
        requested secrets
    """
    config = parse_config(os.path.abspath(os.path.join(os.path.dirname(__file__), "../settings.yml")))
    path = os.path.join(config["vault"]["stack"], config["environment"], config["vault"][connection])
    return get_vault_secret(**config["vault"], path=path)


def get_vault_secret(url, token, path, mount_point, **kwargs):  # pragma: no cover
    """Get vault secrets to certain path in a dictionary.

    Parameters
    ----------
    url : str
        Base URL of Vault server
    token : str
        Token to get access to Vault
    path : str
        Relative path to location of secret
    mount_point : str
        Mount point of address

    Returns
    -------
    dict
        Dictionary with keys and value of a secret
    """
    client = hvac.Client(url=url, token=token)
    if not client.is_authenticated():
        raise VaultError("Vault Authentication Error!")
    response = client.secrets.kv.v1.read_secret(path=path, mount_point=mount_point)
    data = response["data"]
    return data
