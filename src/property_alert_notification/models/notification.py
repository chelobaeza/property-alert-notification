from sqlmodel import SQLModel


class NotificationBase(SQLModel):
    title: str
    message: str
    user_id: int
    user_email: str
    user_phone_number: str



class NotificationCreate(NotificationBase):
    pass


# # Database model
# class Notification(NotificationBase, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int | None = Field(default=None, nullable=False)


# # Properties to return via API
# class NotificationPublic(NotificationBase):
#     pass