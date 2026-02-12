"""Utility functions for Serac integration."""
import re
import unicodedata


def sanitize_entity_id_part(text: str) -> str:
    """Sanitize text for use in entity IDs.

    Removes accents/diacritics and ensures only valid characters.
    Home Assistant entity IDs must contain only lowercase letters, numbers, and underscores.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text safe for entity IDs
    """
    # Normalize unicode characters (decompose accents)
    text = unicodedata.normalize('NFKD', text)
    # Remove diacritics (accent marks)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    # Convert to lowercase
    text = text.lower()
    # Replace any non-alphanumeric characters (except underscore) with underscore
    text = re.sub(r'[^a-z0-9_]+', '_', text)
    # Remove multiple consecutive underscores
    text = re.sub(r'_+', '_', text)
    # Remove leading/trailing underscores
    text = text.strip('_')

    return text
