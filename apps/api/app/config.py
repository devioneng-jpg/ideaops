from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str
    notion_api_key: str
    notion_parent_id: str
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    supabase_url: str
    supabase_service_role_key: str
    database_url: str = ""

    # LLM config
    llm_model: str = "sonnet-4-20250514"
    llm_temperature: float = 0.3


settings = Settings()  # type: ignore[call-arg]
