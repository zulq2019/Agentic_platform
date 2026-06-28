from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "rbac-service"
    service_version: str = "0.1.0"
    contract_version: str = "1.0.0"
    environment: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8002
    log_level: str = "INFO"
    postgres_dsn: str = "postgresql://aep:aep@postgres:5432/aep"
    kafka_bootstrap_servers: str = "kafka:9092"
    redis_url: str = "redis://redis:6379/0"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
