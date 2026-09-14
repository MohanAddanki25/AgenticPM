from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "agentic_pm"
    USE_MOCK_DB_FALLBACK: bool = True

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-this-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    FRONTEND_ORIGIN: str = "http://localhost:5173"
    FRONTEND_ORIGINS: str = ""

    def get_allowed_origins(self) -> list[str]:
        origins = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "https://agentic-pm-8f0g.vercel.app",
            "https://agentic-pm-8foq-5isxbpkv-abcd-4a94.vercel.app",
        }
        if self.FRONTEND_ORIGIN:
            for o in self.FRONTEND_ORIGIN.split(","):
                o = o.strip()
                if o:
                    origins.add(o)
        if self.FRONTEND_ORIGINS:
            for o in self.FRONTEND_ORIGINS.split(","):
                o = o.strip()
                if o:
                    origins.add(o)
        return list(origins)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
