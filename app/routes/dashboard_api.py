from flask import jsonify, request

from app.config.settings import CITY_OPTIONS
from app.core.auth import current_user_id, login_required
from app.services.clothes_service import clothes_row_to_dict, get_user_clothes
from app.services.weather_service import (
    OCCASION_OPTIONS,
    build_outfit_recommendations,
    get_coordinates_by_city,
    get_weather_by_coordinates,
    score_item_for_occasion,
    score_item_for_today,
)


def resolve_weather(city: str):
    city = city.strip() or CITY_OPTIONS[0]
    location_info = get_coordinates_by_city(city)
    weather = None
    resolved_city = city

    if location_info:
        resolved_city = location_info.get("name", city)
        weather = get_weather_by_coordinates(
            location_info["latitude"],
            location_info["longitude"]
        )

    return resolved_city, weather


def register_dashboard_api_routes(app):
    @app.route("/api/dashboard")
    @login_required
    def api_dashboard():
        city = request.args.get("city", CITY_OPTIONS[0]).strip() or CITY_OPTIONS[0]
        resolved_city, weather = resolve_weather(city)

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
            "occasion_options": OCCASION_OPTIONS,
            "today_recommendations": ranked[:5]
        })

    @app.route("/api/recommend_by_occasion")
    @login_required
    def api_recommend_by_occasion():
        city = request.args.get("city", CITY_OPTIONS[0]).strip() or CITY_OPTIONS[0]
        occasion = request.args.get("occasion", "Daily").strip().title()
        if occasion not in OCCASION_OPTIONS:
            occasion = "Daily"

        resolved_city, weather = resolve_weather(city)

        rows = get_user_clothes(current_user_id())
        items = [clothes_row_to_dict(r) for r in rows]

        ranked = []
        for item in items:
            score, reasons = score_item_for_occasion(item, weather, occasion)
            ranked.append({
                **item,
                "score": score,
                "reasons": reasons
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)

        return jsonify({
            "occasion": occasion,
            "city": resolved_city,
            "weather": weather,
            "recommended_items": ranked[:8]
        })

    @app.route("/api/recommend_outfits")
    @login_required
    def api_recommend_outfits():
        city = request.args.get("city", CITY_OPTIONS[0]).strip() or CITY_OPTIONS[0]
        occasion = request.args.get("occasion", "Daily").strip().title()
        if occasion not in OCCASION_OPTIONS:
            occasion = "Daily"

        resolved_city, weather = resolve_weather(city)

        rows = get_user_clothes(current_user_id())
        items = [clothes_row_to_dict(r) for r in rows]

        outfits = build_outfit_recommendations(items, weather, occasion, top_k=5)

        return jsonify({
            "occasion": occasion,
            "city": resolved_city,
            "weather": weather,
            "outfits": outfits
        })