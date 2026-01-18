import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List

from jose import JWTError, jwt
from passlib.context import CryptContext
from supabase import Client, create_client

from app.config import settings


class CustomAuthService:
    """
    Custom Username/Password Authentication Service for FlexTraffs

    IMPORTANT RULES:
    - Users CANNOT register themselves
    - Users CANNOT change passwords
    - Passwords are ADMIN controlled
    - Roles allowed: OPERATOR, OBSERVER
    - Junction-level access is enforced via JWT
    """

    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
        )
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.logger = logging.getLogger(__name__)

        # JWT Settings
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    # ------------------------------------------------------------------
    # PASSWORD HANDLING (ADMIN CONTROLLED)
    # ------------------------------------------------------------------

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    # ------------------------------------------------------------------
    # JUNCTION ACCESS
    # ------------------------------------------------------------------

    def get_user_junctions(self, user_id: int) -> List[int]:
        result = (
            self.supabase
            .table("user_junctions")
            .select("junction_id")
            .eq("user_id", user_id)
            .execute()
        )
        return [row["junction_id"] for row in result.data] if result.data else []

    # ------------------------------------------------------------------
    # AUTHENTICATION
    # ------------------------------------------------------------------

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        try:
            result = (
                self.supabase
                .table("users")
                .select("*")
                .eq("username", username)
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                self.logger.warning(f"User not found: {username}")
                return None

            user = result.data[0]

            if not self.verify_password(password, user["password_hash"]):
                self.logger.warning(f"Invalid password for user: {username}")
                return None

            self.supabase.table("users").update(
                {"last_login": datetime.utcnow().isoformat()}
            ).eq("id", user["id"]).execute()

            return user

        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return None

    # ------------------------------------------------------------------
    # JWT TOKEN CREATION
    # ------------------------------------------------------------------

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )

        junction_ids = self.get_user_junctions(user_data["id"])

        payload = {
            "sub": str(user_data["id"]),
            "username": user_data["username"],
            "role": user_data["role"],
            "junction_ids": junction_ids,
            "exp": expire,
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )

        payload = {
            "sub": str(user_data["id"]),
            "exp": expire,
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    # ------------------------------------------------------------------
    # SESSION MANAGEMENT
    # ------------------------------------------------------------------

    async def create_session(
        self,
        user: Dict[str, Any],
        ip_address: str = None,
        user_agent: str = None,
    ) -> Dict[str, Any]:

        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        session_token = secrets.token_urlsafe(32)

        session_data = {
            "user_id": user["id"],
            "session_token": session_token,
            "refresh_token": refresh_token,
            "expires_at": (
                datetime.utcnow()
                + timedelta(days=self.refresh_token_expire_days)
            ).isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        self.supabase.table("user_sessions").insert(session_data).execute()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_token": session_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
            },
        }

    # ------------------------------------------------------------------
    # TOKEN VERIFICATION
    # ------------------------------------------------------------------

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )

            user_id = payload.get("sub")
            if not user_id:
                return None

            result = (
                self.supabase
                .table("users")
                .select("*")
                .eq("id", int(user_id))
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                return None

            user = result.data[0]
            user["token_data"] = payload
            return user

        except JWTError:
            return None
        except Exception as e:
            self.logger.error(f"Token verification error: {str(e)}")
            return None

    # ------------------------------------------------------------------
    # TOKEN REFRESH
    # ------------------------------------------------------------------

    async def refresh_access_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            if payload.get("type") != "refresh":
                return None

            user_id = payload.get("sub")

            session = (
                self.supabase
                .table("user_sessions")
                .select("*")
                .eq("refresh_token", refresh_token)
                .eq("user_id", int(user_id))
                .gte("expires_at", datetime.utcnow().isoformat())
                .execute()
            )

            if not session.data:
                return None

            user = (
                self.supabase
                .table("users")
                .select("*")
                .eq("id", int(user_id))
                .eq("is_active", True)
                .execute()
            ).data[0]

            new_access_token = self.create_access_token(user)

            self.supabase.table("user_sessions").update(
                {"last_used": datetime.utcnow().isoformat()}
            ).eq("refresh_token", refresh_token).execute()

            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
            }

        except Exception:
            return None

    # ------------------------------------------------------------------
    # LOGOUT
    # ------------------------------------------------------------------

    async def logout(self, session_token: str) -> bool:
        try:
            self.supabase.table("user_sessions").delete().eq(
                "session_token", session_token
            ).execute()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # ADMIN: CREATE USER ONLY
    # ------------------------------------------------------------------

    async def create_user(
        self,
        username: str,
        password: str,
        full_name: str,
        role: str,
    ) -> Optional[Dict[str, Any]]:

        if role not in ["OPERATOR", "OBSERVER"]:
            raise ValueError("Invalid role")

        password_hash = self.hash_password(password)

        user_data = {
            "username": username,
            "password_hash": password_hash,
            "full_name": full_name,
            "role": role,
            "is_active": True,
        }

        result = self.supabase.table("users").insert(user_data).execute()

        if not result.data:
            return None

        user = result.data[0]
        user.pop("password_hash", None)
        return user
