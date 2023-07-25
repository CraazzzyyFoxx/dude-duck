from pydantic import BaseModel, HttpUrl, ConfigDict, Field

__all__ = (
    "AdminGoogleToken",
    "Admin",
    "AdminID",
    "AdminCreate",
    "AdminUpdate"
)


class AdminGoogleToken(BaseModel):
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: int
    auth_uri: HttpUrl
    token_uri: HttpUrl
    auth_provider_x509_cert_url: HttpUrl
    client_x509_cert_url: HttpUrl
    universe_domain: str


class Admin(BaseModel):
    name: str = Field(max_length=20)
    google: AdminGoogleToken


class AdminID(Admin):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token: str


class AdminCreate(Admin):
    pass


class AdminUpdate(Admin):
    pass
