from common.api import create_base_app

from app.api.routes import router
from app.config import OrderServiceSettings

settings = OrderServiceSettings()
app = create_base_app(settings.service_name, api_router=router)
