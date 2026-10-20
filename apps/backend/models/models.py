from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Ingredient(BaseModel):
    quantity: Optional[str] = None
    name: str


class Timer(BaseModel):
    id: str
    label: str
    duration_seconds: int
    step_index: Optional[int] = None
    icon: Optional[str] = None


class TimerCreate(BaseModel):
    label: str
    duration_seconds: int
    step_index: int
    icon: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
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

    ingredients: List[Ingredient] = Field(default_factory=list)
    pantry_ingredients: List[Ingredient] = Field(default_factory=list)

    steps: List[str] = Field(default_factory=list)
    tips: Optional[str] = None

    timers: List[Timer] = Field(default_factory=list)

    cooked_dates: List[str] = Field(default_factory=list)

    image: Optional[str] = None
    image_bytes: Optional[bytes] = Field(default=None, exclude=True)
    image_extension: Optional[str] = Field(default=None, exclude=True)

    category: str = "other"

    search_text: Optional[str] = Field(default=None, exclude=True)
    tokens: List[str] = Field(default_factory=list, exclude=True)

    # Optional fields from Picnic import
    debug_raw_text_path: Optional[str] = Field(default=None, exclude=True)

    model_config = ConfigDict(
        extra="ignore",
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
    )


class RecipeCreate(BaseModel):
    title: str = Field(..., description="Recipe title")

    persons: Optional[int] = Field(None, description="Number of servings")
    time_minutes: Optional[int] = Field(None, description="Preparation time")

    ingredients: List[Ingredient] = Field(default_factory=list)
    pantry_ingredients: List[Ingredient] = Field(default_factory=list)

    steps: List[str] = Field(default_factory=list)
    tips: Optional[str] = None

    image: Optional[str] = None
    category: str = "other"

    is_favorite: bool = False


class RecipeUpdate(BaseModel):
    title: Optional[str] = None

    persons: Optional[int] = None
    time_minutes: Optional[int] = None

    ingredients: Optional[List[Ingredient]] = None
    pantry_ingredients: Optional[List[Ingredient]] = None

    steps: Optional[List[str]] = None
    tips: Optional[str] = None

    image: Optional[str] = None
    category: Optional[str] = None

    is_favorite: Optional[bool] = None


class ProcessPDFRequest(BaseModel):
    pdf_folder: str = "TestRecipes"
    json_out_folder: str = "Recipes/picnic_recipes"
    create_index: bool = True