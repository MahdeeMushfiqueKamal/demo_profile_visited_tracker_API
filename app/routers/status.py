from fastapi import APIRouter


router = APIRouter()


@router.get("/", tags=["General"])
def index():
    return {
        "message": "Welcome to Profile Visit Tracker API",
        "success": True,
    }
