import requests
import time


OCCASION_OPTIONS = ["Daily", "Work", "Sport", "Party", "Formal", "Travel", "Home"]

# 天气缓存
_weather_cache = {}
CACHE_TTL = 600  # 10分钟


def _get_cache_key(lat, lon):
    return f"{round(lat, 2)}_{round(lon, 2)}"


def get_coordinates_by_city(city_name: str):
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        resp = requests.get(url, params=params, timeout=5)
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
    key = _get_cache_key(latitude, longitude)
    now = time.time()

    if key in _weather_cache:
        cached = _weather_cache[key]
        if now - cached["time"] < CACHE_TTL:
            return cached["data"]

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

        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        weather = {
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

        _weather_cache[key] = {
            "time": now,
            "data": weather
        }

        return weather

    except Exception as e:
        print(f"⚠️ 天气获取失败: {e}")
        if key in _weather_cache:
            print("⚠️ 使用旧缓存天气")
            return _weather_cache[key]["data"]
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


def score_item_for_occasion(item: dict, weather: dict | None, occasion: str) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    occasion = (occasion or "Daily").strip().title()
    role = item.get("role") or "Other"
    occasion_tags = item.get("occasion_tags", [])
    season = item.get("season", "All Season")
    thickness = item.get("thickness", "Medium")
    category = (item.get("category_name") or "").lower()

    if occasion in occasion_tags:
        score += 4
        reasons.append(f"适合{occasion}场合")

    if occasion == "Work":
        if role in {"Top", "Bottom", "Outerwear", "Dress", "Shoes"}:
            score += 1
        if any(k in category for k in ["shirt", "blouse", "trouser", "blazer", "coat", "heel", "dress"]):
            score += 2
            reasons.append("风格偏通勤/正式")

    elif occasion == "Sport":
        if any(k in category for k in ["sneaker", "legging", "shorts", "tank", "tee", "t-shirt"]):
            score += 3
            reasons.append("适合运动场景")

    elif occasion == "Party":
        if role in {"Dress", "Top", "Bottom", "Shoes"}:
            score += 1
        if any(k in category for k in ["dress", "skirt", "heel", "blouse"]):
            score += 3
            reasons.append("适合聚会场景")

    elif occasion == "Formal":
        if any(k in category for k in ["blazer", "shirt", "trouser", "heel", "dress", "coat"]):
            score += 3
            reasons.append("适合正式场合")

    elif occasion == "Travel":
        if any(k in category for k in ["hoodie", "sneaker", "jacket", "jean", "coat"]):
            score += 3
            reasons.append("适合出行场景")

    elif occasion == "Home":
        if any(k in category for k in ["hoodie", "sweater", "shorts", "tee", "t-shirt", "knit"]):
            score += 3
            reasons.append("适合居家舒适穿着")

    else:  # Daily
        if "Daily" in occasion_tags:
            score += 2
        if role in {"Top", "Bottom", "Dress", "Outerwear", "Shoes"}:
            score += 1

    temp = weather.get("temperature") if weather else None
    rain_prob = weather.get("precipitation_probability_max") if weather else None

    if temp is not None:
        if temp <= 10:
            if thickness == "Thick" or season == "Autumn/Winter":
                score += 3
                reasons.append("适合低温天气")
        elif 10 < temp <= 20:
            if thickness in {"Medium", "Thick"}:
                score += 2
                reasons.append("适合当前温度")
        else:
            if thickness == "Thin" or season == "Spring/Summer":
                score += 3
                reasons.append("适合温暖天气")

    if rain_prob is not None and rain_prob >= 50:
        if any(k in category for k in ["coat", "jacket", "boot"]):
            score += 2
            reasons.append("适合可能下雨的天气")

    if not reasons:
        reasons.append("场景与天气均较通用")

    return score, reasons[:3]


def get_outfit_templates(occasion: str):
    occasion = (occasion or "Daily").title()
    templates = {
        "Daily": [
            ["Top", "Bottom"],
            ["Dress"],
            ["Top", "Bottom", "Outerwear"]
        ],
        "Work": [
            ["Top", "Bottom"],
            ["Top", "Bottom", "Outerwear"],
            ["Dress", "Outerwear"]
        ],
        "Sport": [
            ["Top", "Bottom"]
        ],
        "Party": [
            ["Dress"],
            ["Top", "Bottom"]
        ],
        "Formal": [
            ["Top", "Bottom", "Outerwear"],
            ["Dress", "Outerwear"],
            ["Top", "Bottom"]
        ],
        "Travel": [
            ["Top", "Bottom"],
            ["Top", "Bottom", "Outerwear"]
        ],
        "Home": [
            ["Top", "Bottom"]
        ]
    }
    return templates.get(occasion, templates["Daily"])


def build_outfit_recommendations(items: list[dict], weather: dict | None, occasion: str, top_k: int = 5):
    occasion = (occasion or "Daily").title()

    scored_items = []
    for item in items:
        score, reasons = score_item_for_occasion(item, weather, occasion)
        scored_items.append({
            **item,
            "occasion_score": score,
            "occasion_reasons": reasons
        })

    by_role = {}
    for item in scored_items:
        role = item.get("role") or "Other"
        by_role.setdefault(role, []).append(item)

    for role_items in by_role.values():
        role_items.sort(key=lambda x: x["occasion_score"], reverse=True)

    outfits = []
    templates = get_outfit_templates(occasion)

    for template in templates:
        if not all(role in by_role and by_role[role] for role in template):
            continue

        chosen = []
        reasons = []
        total_score = 0
        used_ids = set()
        valid = True

        for role in template:
            candidate = None
            for item in by_role[role]:
                if item["id"] not in used_ids:
                    candidate = item
                    break

            if not candidate:
                valid = False
                break

            chosen.append({
                "id": candidate["id"],
                "category_name": candidate["category_name"],
                "image_url": candidate["image_url"],
                "main_category": candidate["main_category"],
                "role": candidate["role"]
            })
            used_ids.add(candidate["id"])
            total_score += candidate["occasion_score"]
            reasons.extend(candidate["occasion_reasons"][:1])

        if not valid:
            continue

        if "Outerwear" in template and weather and (weather.get("temperature") is not None and weather.get("temperature") <= 18):
            total_score += 2
            reasons.append("叠穿更适合当前偏凉天气")

        if template == ["Dress"]:
            reasons.append("单件穿搭更简洁")
        elif template == ["Top", "Bottom"]:
            reasons.append("基础搭配更实用")
        elif "Outerwear" in template:
            reasons.append("层次更完整")

        outfits.append({
            "score": total_score,
            "template": template,
            "items": chosen,
            "reasons": list(dict.fromkeys(reasons))[:3]
        })

    outfits.sort(key=lambda x: x["score"], reverse=True)
    return outfits[:top_k]

