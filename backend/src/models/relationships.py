from sqlalchemy.orm import relationship, foreign
from src.models.api_schemas_model import APISchema
from src.models.etl_config_model import ETLConfig

ETLConfig.schema = relationship(
    APISchema,  # 🔵 Osztálynevet kell megadni nem stringet
    primaryjoin=ETLConfig.source == foreign(APISchema.source),  # 🔵 Igazi python expression
    uselist=False,
    lazy="joined"
)