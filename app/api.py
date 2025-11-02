from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter(prefix="/api", tags=["API"])


# Pydantic models for request/response validation
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    age: int | None = Field(None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.now)


class MessageResponse(BaseModel):
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "success"


class ServerInfo(BaseModel):
    server_name: str
    version: str
    status: str
    uptime: str
    endpoints: list[str]


# In-memory storage for demo purposes
users_db = []


@router.get("/", response_model=MessageResponse)
async def api_root():
    """Root API endpoint"""
    return MessageResponse(message="FastAPI API is running!")


@router.get("/info", response_model=ServerInfo)
async def server_info():
    """Get server information"""
    return ServerInfo(
        server_name="FastAPI Web Server",
        version="1.0.0",
        status="running",
        uptime="0 days",
        endpoints=[
            "/api/",
            "/api/info",
            "/api/users",
            "/api/users/{user_id}",
            "/api/health",
            "/api/echo/{message}",
        ],
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "server": "FastAPI",
        "version": "1.0.0",
    }


@router.get("/users", response_model=list[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
) -> list[User]:
    """Get all users with pagination"""
    return users_db[skip : skip + limit]


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str = Path(..., description="The user ID")) -> User:
    """Get a specific user by ID"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=User)
async def create_user(user: User) -> User:
    """Create a new user"""
    # Check if email already exists
    if any(u.email == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already exists")

    users_db.append(user)
    return user


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    updated_user: User, user_id: str = Path(..., description="The user ID")
) -> User:
    """Update an existing user"""
    user_index = next((i for i, u in enumerate(users_db) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email already exists (excluding current user)
    if any(u.email == updated_user.email and u.id != user_id for u in users_db):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Update user while preserving ID and creation date
    updated_user.id = user_id
    updated_user.created_at = users_db[user_index].created_at
    users_db[user_index] = updated_user

    return updated_user


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str = Path(..., description="The user ID"),
) -> MessageResponse:
    """Delete a user"""
    user_index = next((i for i, u in enumerate(users_db) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="User not found")

    users_db.pop(user_index)
    return MessageResponse(message=f"User {user_id} deleted successfully")


@router.get("/echo/{message}")
async def echo_message(
    message: str = Path(..., description="Message to echo"),
    repeat: int = Query(1, ge=1, le=10, description="Number of times to repeat"),
):
    """Echo a message with optional repetition"""
    return {
        "original_message": message,
        "repeated_message": " ".join([message] * repeat),
        "length": len(message),
        "timestamp": datetime.now(),
    }


@router.get("/math/square/{number}")
async def square_number(number: float = Path(..., description="Number to square")):
    """Calculate the square of a number"""
    return {"number": number, "square": number**2, "operation": "square"}


@router.get("/math/cube/{number}")
async def cube_number(number: float = Path(..., description="Number to cube")):
    """Calculate the cube of a number"""
    return {"number": number, "cube": number**3, "operation": "cube"}


# Add some sample users for demonstration
def add_sample_users():
    """Add sample users to the database"""
    sample_users = [
        User(name="John Doe", email="john@example.com", age=30),
        User(name="Jane Smith", email="jane@example.com", age=25),
        User(name="Bob Johnson", email="bob@example.com", age=35),
    ]
    users_db.extend(sample_users)


# Add sample users when module is imported
add_sample_users()
