import requests


def get_coordinates_by_city(city_name: str):
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return None

        return {
            "name": results[0].get("name", city_name),
            "latitude": results[0]["latitude"],
            "longitude": results[0]["longitude"],
            "country": results[0].get("country", "")
        }
    except Exception as e:
        print(f"⚠️ 地理编码失败: {e}")
        return None


def get_weather_by_coordinates(latitude: float, longitude: float):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code",
            "daily": "precipitation_probability_max,temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "forecast_days": 1
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        return {
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "precipitation": current.get("precipitation"),
            "rain": current.get("rain"),
            "showers": current.get("showers"),
            "snowfall": current.get("snowfall"),
            "weather_code": current.get("weather_code"),
            "precipitation_probability_max": (
                daily.get("precipitation_probability_max", [None])[0]
                if daily.get("precipitation_probability_max") else None
            ),
            "temp_max": (
                daily.get("temperature_2m_max", [None])[0]
                if daily.get("temperature_2m_max") else None
            ),
            "temp_min": (
                daily.get("temperature_2m_min", [None])[0]
                if daily.get("temperature_2m_min") else None
            )
        }
    except Exception as e:
        print(f"⚠️ 天气获取失败: {e}")
        return None


def score_item_for_today(item: dict, weather: dict | None) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    category = (item.get("category_name") or "").lower()
    attrs = [a.lower() for a in item.get("attribute_names", [])]
    season = item.get("season", "All Season")
    thickness = item.get("thickness", "Medium")

    if not weather:
        if season == "All Season":
            score += 1
            reasons.append("适合日常天气")
        return score, reasons

    temp = weather.get("temperature")
    rain_prob = weather.get("precipitation_probability_max")

    if temp is not None:
        if temp <= 10:
            if thickness == "Thick" or season == "Autumn/Winter":
                score += 3
                reasons.append("适合低温天气")
        elif 10 < temp <= 20:
            if thickness in {"Medium", "Thick"}:
                score += 2
                reasons.append("适合偏凉天气")
        else:
            if thickness == "Thin" or season == "Spring/Summer":
                score += 3
                reasons.append("适合温暖天气")

    if rain_prob is not None and rain_prob >= 50:
        if any(k in category for k in ["coat", "jacket"]) or any("black" in a or "dark" in a for a in attrs):
            score += 2
            reasons.append("适合可能下雨的天气")

    if not reasons:
        reasons.append("基础百搭")

    return score, reasons