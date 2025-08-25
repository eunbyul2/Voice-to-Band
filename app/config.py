
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    LOG_LEVEL: str = "info"
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # STT
    STT_MODEL: str = "tiny"
    STT_DEVICE: str = "cpu"              # "cpu" or "cuda"
    STT_COMPUTE_TYPE: str = "int8"       # "int8", "int8_float16", "fp16", ...

    # Piper
    PIPER_PATH: str | None = None
    PIPER_MODEL: str | None = None
    PIPER_SPEAKER: int = 0

    # CREPE
    CREPE_ONNX_PATH: str | None = None

settings = Settings()
