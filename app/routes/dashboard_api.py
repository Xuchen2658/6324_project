from flask import jsonify, request

from app.config.settings import CITY_OPTIONS
from app.core.auth import current_user_id, login_required
from app.services.clothes_service import clothes_row_to_dict, get_user_clothes
from app.services.weather_service import (
    get_coordinates_by_city,
    get_weather_by_coordinates,
    score_item_for_today,
)


def register_dashboard_api_routes(app):
    @app.route("/api/dashboard")
    @login_required
    def api_dashboard():
        city = request.args.get("city", CITY_OPTIONS[0]).strip() or CITY_OPTIONS[0]

        location_info = get_coordinates_by_city(city)
        weather = None
        resolved_city = city

        if location_info:
            resolved_city = location_info.get("name", city)
            weather = get_weather_by_coordinates(
                location_info["latitude"],
                location_info["longitude"]
            )

        rows = get_user_clothes(current_user_id())
        items = [clothes_row_to_dict(r) for r in rows]

        ranked = []
        for item in items:
            score, reasons = score_item_for_today(item, weather)
            ranked.append({
                **item,
                "score": score,
                "reasons": reasons[:2]
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)

        return jsonify({
            "city_options": CITY_OPTIONS,
            "city": resolved_city,
            "weather": weather,
            "today_recommendations": ranked[:5]
        })