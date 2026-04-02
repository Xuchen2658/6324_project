from app.routes.dashboard_api import register_dashboard_api_routes
from app.routes.deleted_api import register_deleted_api_routes
from app.routes.pages import register_page_routes
from app.routes.upload_api import register_upload_api_routes
from app.routes.user_api import register_user_api_routes
from app.routes.wardrobe_api import register_wardrobe_api_routes


def register_routes(app):
    register_page_routes(app)
    register_user_api_routes(app)
    register_wardrobe_api_routes(app)
    register_deleted_api_routes(app)
    register_dashboard_api_routes(app)
    register_upload_api_routes(app)