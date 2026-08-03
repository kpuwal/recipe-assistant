class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_http_exception(self):
        from fastapi import HTTPException
        return HTTPException(status_code=self.status_code, detail=self.message)


class RecipeNotFound(AppError):
    def __init__(self, recipe_id: str):
        super().__init__(f"Recipe not found: {recipe_id}", status_code=404)


class PDFParseError(AppError):
    def __init__(self, message: str = "Failed to parse PDF"):
        from starlette import status
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AIServiceError(AppError):
    def __init__(self, message: str = "AI service temporarily unavailable"):
        super().__init__(message, status_code=502)
