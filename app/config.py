from datetime import time

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ticktick_access_token: str = ""
    ticktick_base_url: str = "https://api.ticktick.com/open/v1"
    ticktick_default_project_id: str = "inbox"
    protected_projects: str = "Appointment"

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    working_hours_start: str = "09:00"
    working_hours_end: str = "18:00"
    min_task_duration_minutes: int = 15
    max_task_duration_minutes: int = 180
    scheduling_buffer_minutes: int = 10
    default_timezone: str = "Asia/Manila"

    @property
    def protected_project_list(self) -> list[str]:
        return [p.strip() for p in self.protected_projects.split(",") if p.strip()]

    def is_protected_project(
        self, project_id: str | None, project_name: str | None
    ) -> bool:
        protected_names = {
            name.casefold() for name in self.protected_project_list
        } | {"appointment", "appointments"}
        protected_ids = {"appointment", "appointments"}
        return (
            project_id is not None
            and str(project_id).strip().casefold() in protected_ids
        ) or (
            project_name is not None
            and str(project_name).strip().casefold() in protected_names
        )

    @property
    def working_start_time(self) -> time:
        h, m = map(int, self.working_hours_start.split(":"))
        return time(h, m)

    @property
    def working_end_time(self) -> time:
        h, m = map(int, self.working_hours_end.split(":"))
        return time(h, m)


settings = Settings()
