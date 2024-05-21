from sqlmodel import Field, SQLModel


class PreferenceBase(SQLModel):
    email_enabled: bool
    sms_enabled: bool


class PreferenceCreate(PreferenceBase):
    pass


# Database model
class Preference(PreferenceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, nullable=False, unique=True)


# Properties to return via API
class PreferencePublic(PreferenceBase):
    pass