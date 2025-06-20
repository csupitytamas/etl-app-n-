from sqlalchemy.orm import relationship, foreign
from src.models.api_schemas_model import APISchema
from src.models.auth_model import  UserSession
from src.models.etl_config_model import ETLConfig
from src.models.users_model import User

ETLConfig.schema = relationship(
    APISchema,
    primaryjoin=ETLConfig.source == foreign(APISchema.source),
    uselist=False,
    lazy="joined"
)

User.sessions = relationship(
    UserSession,
    back_populates="user",
    cascade="all, delete-orphan"
)