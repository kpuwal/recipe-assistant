from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from pydantic import ConfigDict


class Ingredient(BaseModel):
    quantity: Optional[str] = None
    name: str


class ChatRequest(BaseModel):  # kept for completeness
    message: str
    session_id: Optional[str] = "default"
    language: str = "nl"


class Recipe(BaseModel):
    id: Optional[str] = None
    slug: Optional[str] = None
    title: str
    source: str = "personal"

    is_favorite: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    processed_at: Optional[str] = None
    
    persons: Optional[int] = None
    time_minutes: Optional[int] = None

    ingredients: List[Ingredient] = []
    pantry_ingredients: List[Ingredient] = []

    steps: List[str] = []
    tips: Optional[str] = None

    image: Optional[str] = None
    image_bytes: Optional[bytes] = None
    image_extension: Optional[str] = None

    category: Optional[str] = "other"
    search_text: Optional[str] = None
    tokens: List[str] = []

    # Optional fields from picnic
    debug_raw_text_path: Optional[str] = None

    model_config = ConfigDict(
        extra="ignore",
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class ProcessPDFRequest(BaseModel):
    pdf_folder: str = "TestRecipes"
    json_out_folder: str = "Recipes/picnic_recipes"
    create_index: bool = True
