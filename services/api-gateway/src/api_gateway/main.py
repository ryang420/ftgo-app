from common.api import create_base_app

from api_gateway.api.routes import router
from api_gateway.config import get_settings

settings = get_settings()
app = create_base_app(settings.service_name, api_router=router)
