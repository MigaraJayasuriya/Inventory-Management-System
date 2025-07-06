from datetime import UTC, timedelta, datetime
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from .database import SessionLocal
from .models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends, HTTPException

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = 'your_secret_key_here'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: Session = Depends(get_db)):
    create_user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        is_superuser=0,
        is_active=1
    )

    db.add(create_user_model)
    db.commit()
    return {"message": "User created successfully"}

@router.post("/token", response_model=Token)
async def Login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(user.username, user.is_superuser, user.id, timedelta(minutes=30))

    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, is_superuser: bool, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'is_superuser': is_superuser, 'user_id': user_id}
    expires = datetime.now(UTC) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_superuser: bool = payload.get("is_superuser")
        user_id: int = payload.get("user_id")
        if username is None or is_superuser is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"username": username, "is_superuser": is_superuser, "user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
 


