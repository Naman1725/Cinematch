"""Authentication routes"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_password_reset_token
)
from app.models.user import User, AuthProvider, UserRole
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    PasswordReset,
    PasswordResetConfirm,
    OAuthUserCreate
)
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_verified=False,
        role=UserRole.USER,
        last_login=datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/oauth/google", response_model=Token)
async def google_oauth(
    user_data: OAuthUserCreate,
    db: Session = Depends(get_db)
):
    """Google OAuth login/register"""
    # Check if user exists
    user = db.query(User).filter(
        (User.email == user_data.email) |
        ((User.oauth_id == user_data.oauth_id) & (User.auth_provider == AuthProvider.GOOGLE))
    ).first()

    if user:
        # Update existing user
        user.last_login = datetime.utcnow()
        if not user.avatar_url and user_data.avatar_url:
            user.avatar_url = user_data.avatar_url
    else:
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            avatar_url=user_data.avatar_url,
            auth_provider=AuthProvider.GOOGLE,
            oauth_id=user_data.oauth_id,
            is_active=True,
            is_verified=True,  # OAuth users are pre-verified
            role=UserRole.USER,
            last_login=datetime.utcnow()
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/oauth/github", response_model=Token)
async def github_oauth(
    user_data: OAuthUserCreate,
    db: Session = Depends(get_db)
):
    """GitHub OAuth login/register"""
    # Check if user exists
    user = db.query(User).filter(
        (User.email == user_data.email) |
        ((User.oauth_id == user_data.oauth_id) & (User.auth_provider == AuthProvider.GITHUB))
    ).first()

    if user:
        # Update existing user
        user.last_login = datetime.utcnow()
        if not user.avatar_url and user_data.avatar_url:
            user.avatar_url = user_data.avatar_url
    else:
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            avatar_url=user_data.avatar_url,
            auth_provider=AuthProvider.GITHUB,
            oauth_id=user_data.oauth_id,
            is_active=True,
            is_verified=True,
            role=UserRole.USER,
            last_login=datetime.utcnow()
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    user = db.query(User).filter(User.email == data.email).first()

    if user and user.auth_provider == AuthProvider.LOCAL:
        # Generate reset token
        reset_token = create_password_reset_token(user.email)

        # TODO: Send email with reset token
        # For now, just return success
        # In production, you would send an email here

        return {"message": "Password reset email sent"}

    # Always return success for security
    return {"message": "Password reset email sent"}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    email = verify_password_reset_token(data.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Password reset successful"}
