from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "SIMRS TTE BSRE Microservice"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database PostgreSQL Microservice (Wajib dari .env)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Database MySQL Riil SIMRS (Read-Only / SELECT Only — Wajib dari .env)
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # JWT Security (Wajib dari .env)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # ClamAV Antivirus
    CLAMAV_ENABLED: bool = os.getenv("CLAMAV_ENABLED", "true").lower() == "true"
    CLAMAV_HOST: str = os.getenv("CLAMAV_HOST", "localhost")
    CLAMAV_PORT: int = int(os.getenv("CLAMAV_PORT", "3310"))

    # BSrE BSSN Integration Config (Semua rahasia wajib dari .env)
    BSRE_BASE_URL: str = os.getenv("BSRE_BASE_URL", "")
    BSRE_USERNAME: str = os.getenv("BSRE_USERNAME", "")
    BSRE_PASSWORD: str = os.getenv("BSRE_PASSWORD", "")
    BSRE_MOCK_MODE: bool = os.getenv("BSRE_MOCK_MODE", "true").lower() == "true"
    BSRE_TIMEOUT_SECONDS: int = int(os.getenv("BSRE_TIMEOUT_SECONDS", "15"))

    # Kredensial Uji Coba User Dev dari Kominfo (Wajib dari .env)
    BSRE_DEV_NIK: str = os.getenv("BSRE_DEV_NIK", "")
    BSRE_DEV_PASSPHRASE: str = os.getenv("BSRE_DEV_PASSPHRASE", "")

    # Hospital Info Resmi
    HOSPITAL_GOV_HEADER: str = os.getenv("HOSPITAL_GOV_HEADER", "PEMERINTAH KOTA PROBOLINGGO")
    HOSPITAL_NAME: str = os.getenv("HOSPITAL_NAME", "UOBK RSUD DOKTER MOHAMAD SALEH")
    HOSPITAL_CITY: str = os.getenv("HOSPITAL_CITY", "PROBOLINGGO")
    HOSPITAL_ADDRESS: str = os.getenv("HOSPITAL_ADDRESS", "Jl. Mayjend Panjaitan No.65 Probolinggo Jawa Timur")
    HOSPITAL_PHONE: str = os.getenv("HOSPITAL_PHONE", "Telp. (0335) 433478,433119,421118 Fax. (0335) 432702")
    HOSPITAL_EMAIL: str = os.getenv("HOSPITAL_EMAIL", "rsudprob@probolinggokota.go.id")

    # Storage Paths
    BASE_STORAGE_PATH: str = os.getenv(
        "BASE_STORAGE_PATH",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "app")
    )

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
