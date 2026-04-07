import requests
import time


OCCASION_OPTIONS = ["Daily", "Work", "Sport", "Party", "Formal", "Travel", "Home"]

_weather_cache = {}
CACHE_TTL = 600  # 10 minutes


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


# =========================
# 基础打分
# =========================

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
    attrs = [a.lower() for a in item.get("attribute_names", [])]

    if occasion in occasion_tags:
        score += 4
        reasons.append(f"适合{occasion}场合")

    # 场合偏好
    if occasion == "Work":
        if role in {"Top", "Bottom", "Outerwear", "Dress", "Shoes"}:
            score += 1
        if any(k in category for k in ["shirt", "blouse", "trouser", "blazer", "coat", "heel", "dress"]):
            score += 3
            reasons.append("风格偏通勤/正式")
        if any(k in category for k in ["shorts", "tank", "hoodie"]):
            score -= 3

    elif occasion == "Sport":
        if any(k in category for k in ["sneaker", "legging", "shorts", "tank", "tee", "t-shirt"]):
            score += 4
            reasons.append("适合运动场景")
        if any(k in category for k in ["blazer", "heel", "coat", "dress"]):
            score -= 3

    elif occasion == "Party":
        if role in {"Dress", "Top", "Bottom", "Shoes"}:
            score += 1
        if any(k in category for k in ["dress", "skirt", "heel", "blouse"]):
            score += 4
            reasons.append("适合聚会场景")
        if any(k in category for k in ["sport", "legging"]) or "cloth_type: two_piece" in attrs and "tank" in category:
            score -= 2

    elif occasion == "Formal":
        if any(k in category for k in ["blazer", "shirt", "trouser", "heel", "dress", "coat"]):
            score += 4
            reasons.append("适合正式场合")
        if any(k in category for k in ["hoodie", "shorts", "sneaker"]):
            score -= 3

    elif occasion == "Travel":
        if any(k in category for k in ["hoodie", "sneaker", "jacket", "jean", "coat", "pants"]):
            score += 4
            reasons.append("适合出行场景")
        if any(k in category for k in ["heel", "formal dress"]):
            score -= 2

    elif occasion == "Home":
        if any(k in category for k in ["hoodie", "sweater", "shorts", "tee", "t-shirt", "knit", "pants"]):
            score += 4
            reasons.append("适合居家舒适穿着")
        if any(k in category for k in ["heel", "blazer"]):
            score -= 3

    else:  # Daily
        if "Daily" in occasion_tags:
            score += 2
        if role in {"Top", "Bottom", "Dress", "Outerwear", "Shoes"}:
            score += 1
        if any(k in category for k in ["shirt", "pants", "jeans", "hoodie", "sneaker", "dress"]):
            score += 1

    # 天气适配
    temp = weather.get("temperature") if weather else None
    rain_prob = weather.get("precipitation_probability_max") if weather else None

    if temp is not None:
        if temp <= 10:
            if thickness == "Thick" or season == "Autumn/Winter":
                score += 3
                reasons.append("适合低温天气")
            elif thickness == "Thin":
                score -= 2
        elif 10 < temp <= 20:
            if thickness in {"Medium", "Thick"}:
                score += 2
                reasons.append("适合当前温度")
        else:
            if thickness == "Thin" or season == "Spring/Summer":
                score += 3
                reasons.append("适合温暖天气")
            elif thickness == "Thick":
                score -= 2

    if rain_prob is not None and rain_prob >= 50:
        if any(k in category for k in ["coat", "jacket", "boot"]):
            score += 2
            reasons.append("适合可能下雨的天气")
        if any(k in category for k in ["sandal", "heel"]):
            score -= 1

    if not reasons:
        reasons.append("场景与天气均较通用")

    return score, reasons[:3]


# =========================
# 穿搭模板
# =========================

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
            ["Top", "Bottom"],
            ["Dress", "Outerwear"]
        ],
        "Formal": [
            ["Top", "Bottom", "Outerwear"],
            ["Dress", "Outerwear"],
            ["Top", "Bottom"]
        ],
        "Travel": [
            ["Top", "Bottom"],
            ["Top", "Bottom", "Outerwear"],
            ["Dress", "Outerwear"]
        ],
        "Home": [
            ["Top", "Bottom"]
        ]
    }
    return templates.get(occasion, templates["Daily"])


# =========================
# 辅助规则
# =========================

def _extract_color_names(item: dict):
    attrs = [a.lower() for a in item.get("attribute_names", [])]
    colors = []

    for attr in attrs:
        if attr.startswith("color:"):
            raw = attr.replace("color:", "").strip()
            parts = [x.strip() for x in raw.split("+")]
            for p in parts:
                if p and p not in colors:
                    colors.append(p)
    return colors


def _is_neutral_color(color: str) -> bool:
    return color in {"black", "white", "gray", "beige", "brown"}


def _color_compatibility_score(items: list[dict]) -> tuple[int, list[str]]:
    colors = []
    for item in items:
        colors.extend(_extract_color_names(item))

    colors = [c for c in colors if c]
    if not colors:
        return 0, []

    unique_colors = list(dict.fromkeys(colors))

    if len(unique_colors) == 1:
        return 2, ["颜色风格统一"]

    if all(_is_neutral_color(c) for c in unique_colors):
        return 2, ["颜色较百搭"]

    if len(unique_colors) == 2:
        if any(_is_neutral_color(c) for c in unique_colors):
            return 2, ["颜色搭配较协调"]
        return 1, ["颜色有一定层次"]

    # 太多颜色略扣分
    return -1, ["颜色组合偏复杂"]


def _thickness_value(thickness: str) -> int:
    thickness = (thickness or "").lower()
    if "thin" in thickness:
        return 1
    if "medium" in thickness:
        return 2
    if "thick" in thickness:
        return 3
    return 2


def _temperature_layer_score(template: list[str], items: list[dict], weather: dict | None) -> tuple[int, list[str]]:
    if not weather or weather.get("temperature") is None:
        return 0, []

    temp = weather["temperature"]
    reasons = []
    score = 0

    avg_thickness = sum(_thickness_value(i.get("thickness", "Medium")) for i in items) / max(len(items), 1)
    has_outerwear = "Outerwear" in template
    has_dress = "Dress" in template
    has_top_bottom = ("Top" in template and "Bottom" in template)

    if temp <= 10:
        if has_outerwear:
            score += 2
            reasons.append("叠穿更适合低温天气")
        if avg_thickness >= 2.3:
            score += 2
        if has_dress and not has_outerwear:
            score -= 2

    elif 10 < temp <= 20:
        if has_outerwear:
            score += 1
            reasons.append("适合偏凉天气")
        if 1.8 <= avg_thickness <= 2.6:
            score += 1

    else:
        if has_outerwear:
            score -= 2
        if avg_thickness <= 1.7:
            score += 2
            reasons.append("整体更适合温暖天气")
        if has_dress and not has_outerwear:
            score += 1
        if has_top_bottom:
            score += 1

    return score, reasons


def _cloth_type_score(template: list[str], items: list[dict]) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    attrs = []
    for item in items:
        attrs.extend([a.lower() for a in item.get("attribute_names", [])])

    cloth_type_text = " ".join(attrs)

    if "Dress" in template:
        # dress outfit should not look like separated upper/lower set
        if "cloth_type: single" in cloth_type_text:
            score += 2
            reasons.append("单件穿搭更简洁")
    elif "Top" in template and "Bottom" in template:
        if "cloth_type: two_piece" in cloth_type_text:
            score += 1
            reasons.append("更符合上下装搭配")

    return score, reasons


def _occasion_consistency_penalty(occasion: str, items: list[dict]) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    categories = " ".join((i.get("category_name") or "").lower() for i in items)

    if occasion == "Work":
        if any(k in categories for k in ["shorts", "tank", "hoodie"]):
            score -= 3
            reasons.append("部分单品不够适合通勤")
    elif occasion == "Formal":
        if any(k in categories for k in ["hoodie", "shorts", "sneaker"]):
            score -= 4
            reasons.append("部分单品不够正式")
    elif occasion == "Sport":
        if any(k in categories for k in ["blazer", "heel", "coat"]):
            score -= 4
            reasons.append("部分单品不够适合运动")
    elif occasion == "Home":
        if any(k in categories for k in ["heel", "blazer"]):
            score -= 3
            reasons.append("部分单品不够适合居家")

    return score, reasons


# =========================
# 穿搭生成
# =========================

def build_outfit_recommendations(items: list[dict], weather: dict | None, occasion: str, top_k: int = 5):
    occasion = (occasion or "Daily").title()

    # 先给单件打分
    scored_items = []
    for item in items:
        score, reasons = score_item_for_occasion(item, weather, occasion)
        scored_items.append({
            **item,
            "occasion_score": score,
            "occasion_reasons": reasons
        })

    # 分组
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

        # 从每个 role 里取前几个做组合尝试，而不是只取第一个
        candidate_lists = []
        for role in template:
            candidate_lists.append(by_role[role][:3])

        # 简单笛卡尔组合（最多 3^3，仍很小）
        def backtrack(idx, chosen, used_ids):
            if idx == len(template):
                outfits.append(_build_one_outfit(chosen, template, weather, occasion))
                return

            for item in candidate_lists[idx]:
                if item["id"] in used_ids:
                    continue
                chosen.append(item)
                used_ids.add(item["id"])
                backtrack(idx + 1, chosen, used_ids)
                chosen.pop()
                used_ids.remove(item["id"])

        backtrack(0, [], set())

    # 过滤 None
    outfits = [o for o in outfits if o is not None]

    # 去重：按 item id 组合去重
    dedup = {}
    for outfit in outfits:
        key = tuple(sorted(x["id"] for x in outfit["items"]))
        if key not in dedup or outfit["score"] > dedup[key]["score"]:
            dedup[key] = outfit

    final_outfits = list(dedup.values())
    final_outfits.sort(key=lambda x: x["score"], reverse=True)
    return final_outfits[:top_k]


def _build_one_outfit(chosen_items: list[dict], template: list[str], weather: dict | None, occasion: str):
    if not chosen_items:
        return None

    total_score = 0
    reasons = []

    for item in chosen_items:
        total_score += item["occasion_score"]
        reasons.extend(item["occasion_reasons"][:1])

    # 颜色协调
    color_score, color_reasons = _color_compatibility_score(chosen_items)
    total_score += color_score
    reasons.extend(color_reasons)

    # 温度与层次
    temp_score, temp_reasons = _temperature_layer_score(template, chosen_items, weather)
    total_score += temp_score
    reasons.extend(temp_reasons)

    # cloth_type 规则
    cloth_score, cloth_reasons = _cloth_type_score(template, chosen_items)
    total_score += cloth_score
    reasons.extend(cloth_reasons)

    # 场合一致性惩罚
    occasion_penalty, occasion_reasons = _occasion_consistency_penalty(occasion, chosen_items)
    total_score += occasion_penalty
    reasons.extend(occasion_reasons)

    # 模板基础奖励
    if template == ["Dress"]:
        total_score += 1
        reasons.append("单件搭配更省心")
    elif template == ["Top", "Bottom"]:
        total_score += 1
        reasons.append("基础搭配更实用")
    elif "Outerwear" in template:
        total_score += 1
        reasons.append("层次更完整")

    items_brief = []
    for candidate in chosen_items:
        items_brief.append({
            "id": candidate["id"],
            "category_name": candidate["category_name"],
            "image_url": candidate["image_url"],
            "main_category": candidate["main_category"],
            "role": candidate["role"]
        })

    return {
        "score": int(total_score),
        "template": template,
        "items": items_brief,
        "reasons": list(dict.fromkeys(reasons))[:4]
    }