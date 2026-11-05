import unicodedata


def normalize(text: str) -> str:
    """Minúsculas y sin tildes, para comparar palabras clave («Cuánto» = «cuanto»)."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
