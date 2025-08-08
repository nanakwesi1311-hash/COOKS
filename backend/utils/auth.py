# utils/auth.py
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.db_utils import get_user_by_username
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return {"username": user["username"], "role": user["role"]}

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        user = get_user_by_username(username)
        if not user:
            raise credentials_exception

        return {"username": user["username"], "role": user["role"]}  # ✅ Include role
    except PyJWTError:
        raise credentials_exception
