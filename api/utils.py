import re
from urllib.parse import urlparse

from config import CONF_MAPPER
from dtos import ConfName


def matches_pattern(pattern: str, string: str) -> bool:
    """
    checks if a given string matches a specified pattern

    Args:
        pattern (str): pattern to match, supports '*' wildcard
        string (str): string to be matched against the pattern

    Returns:
        bool: whether the string matches the pattern
    """
    if pattern.endswith('*/'):
        if pattern.startswith('*'):
            pattern = pattern[1:]
        escaped_pattern = re.escape(pattern).replace(r'\*', '[^/]*')
        escaped_pattern = ".*" + escaped_pattern
    else:
        escaped_pattern = re.escape(pattern).replace(r'\*', '.*')
    regex_pattern = f'^{escaped_pattern}$'
    return bool(re.match(regex_pattern, string))


def get_configuration_name(url: str) -> ConfName:
    """
    retrieves the configuration name corresponding to a URL

    Args:
        url (str): URL for which the configuration name is determined

    Returns:
        ConfName: configuration name corresponding to the URL or ConfName.UNKNOWN if no match is found
    """
    for key, value in CONF_MAPPER.items():
        if matches_pattern(key, url):
            return value
    return ConfName.UNKNOWN

def display_dict(data: dict) -> dict:
    """
    transformes all dictionary values to strings and slices them to 100 characters, used for displaying purposes

    Args:
        data (dict): input dictionary

    Returns:
        dict: transformed dictionary or input data if its format is not a dict
    """
    if isinstance(data, dict):
        truncated_data = {key: (str(value)[:100] + "..." if len(str(value)) > 100 else str(value)) for key, value in data.items()}
        return truncated_data
    return data

def get_domain(url):
    """ extracts domain from url """
    try:
        return urlparse(url).hostname
    except Exception:
        return None