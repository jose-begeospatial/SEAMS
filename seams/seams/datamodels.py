from typing import Optional
from pydantic import BaseModel, EmailStr



class Users(BaseModel):
    """Define a Pydantic model for the Users table

    Args:
        BaseModel (_type_): _description_
    """
    name: str
    email: EmailStr
    affiliation: str
