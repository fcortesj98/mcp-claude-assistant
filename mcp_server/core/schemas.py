"""Pydantic schemas used for structured user elicitation."""

from pydantic import BaseModel


class DocumentGeneratorSchema(BaseModel):
    """Inputs elicited from the user by the ``documentation_generator`` prompt.

    Attributes:
        file_path: Path of the file to generate documentation for.
        name: Name of the documentation file to create.
    """

    file_path: str
    name: str
