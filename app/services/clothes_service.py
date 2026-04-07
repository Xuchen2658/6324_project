import json

from app.core.database import get_db


def infer_main_category(category_name: str, attribute_names: list[str]) -> str:
    cat = (category_name or "").lower()
    attrs = [a.lower() for a in attribute_names]

    if "dress" in cat:
        return "Skirts"
    if any(k in cat for k in ["shoe", "sneaker", "boot", "heel", "sandal", "loafer"]):
        return "Shoes"
    if any(k in cat for k in ["hat", "cap", "beanie"]):
        return "Hats"
    if any(k in cat for k in ["skirt"]):
        return "Skirts"
    if any(k in cat for k in ["pant", "jean", "trouser", "shorts", "legging"]):
        return "Pants"
    if any(k in cat for k in ["sweater", "knit", "cardigan"]):
        return "Sweaters"
    if any(k in cat for k in ["coat", "jacket", "hoodie", "outerwear", "blazer"]):
        return "Outerwear"
    if any("short sleeve" in a for a in attrs):
        return "Short Sleeve"
    if any("long sleeve" in a for a in attrs):
        return "Long Sleeve"
    if any(k in cat for k in ["shirt", "top", "blouse", "tee", "t-shirt", "tank", "pullover"]):
        return "Tops"

    return "Others"


def infer_extra_tags(category_name: str, attribute_names: list[str]) -> dict:
    cat = (category_name or "").lower()
    attrs = [a.lower() for a in attribute_names]

    season = "All Season"
    thickness = "Medium"

    if any(k in cat for k in ["coat", "jacket", "sweater", "hoodie", "blazer", "cardigan"]):
        season = "Autumn/Winter"
        thickness = "Thick"
    elif any(k in cat for k in ["t-shirt", "tee", "tank", "shorts", "skirt", "dress"]):
        season = "Spring/Summer"
        thickness = "Thin"

    if any("long sleeve" in a for a in attrs):
        thickness = "Medium"

    return {
        "season": season,
        "thickness": thickness
    }


def infer_role(category_name: str, main_category: str, attribute_names: list[str]) -> str:
    cat = (category_name or "").lower()
    main = (main_category or "").lower()
    attrs = [a.lower() for a in attribute_names]

    if "dress" in cat:
        return "Dress"
    if main in {"tops", "short sleeve", "long sleeve", "sweaters"}:
        return "Top"
    if main in {"pants", "skirts"}:
        return "Bottom"
    if main == "outerwear":
        return "Outerwear"
    if main == "shoes":
        return "Shoes"
    if main == "hats":
        return "Hat"

    if any(k in cat for k in ["shirt", "top", "blouse", "tee", "t-shirt", "tank", "pullover"]):
        return "Top"
    if any(k in cat for k in ["pant", "jean", "trouser", "shorts", "legging", "skirt"]):
        return "Bottom"
    if any(k in cat for k in ["coat", "jacket", "hoodie", "cardigan", "blazer"]):
        return "Outerwear"
    if any(k in cat for k in ["shoe", "sneaker", "boot", "heel", "sandal"]):
        return "Shoes"

    if any("dress" in a for a in attrs):
        return "Dress"

    return "Other"


def infer_occasion_tags(category_name: str, main_category: str, attribute_names: list[str]) -> list[str]:
    cat = (category_name or "").lower()
    main = (main_category or "").lower()
    attrs = [a.lower() for a in attribute_names]

    tags = set()

    if any(k in cat for k in ["hoodie", "jean", "t-shirt", "tee", "shirt", "sneaker", "coat", "jacket"]):
        tags.update(["Daily", "Travel"])

    if any(k in cat for k in ["blazer", "shirt", "blouse", "trouser", "heel", "coat", "dress"]):
        tags.update(["Work", "Formal"])

    if any(k in cat for k in ["dress", "skirt", "heel", "blouse"]):
        tags.add("Party")

    if any(k in cat for k in ["tank", "legging", "shorts", "sneaker"]):
        tags.add("Sport")

    if any(k in cat for k in ["hoodie", "sweater", "knit", "cardigan", "shorts", "tee", "t-shirt"]):
        tags.add("Home")

    if main in {"tops", "short sleeve", "long sleeve"}:
        tags.add("Daily")
    if main == "outerwear":
        tags.update(["Daily", "Work", "Travel"])
    if main == "pants":
        tags.update(["Daily", "Work"])
    if main == "skirts":
        tags.update(["Daily", "Party"])
    if main == "shoes":
        tags.update(["Daily", "Travel"])

    if any("long sleeve" in a for a in attrs):
        tags.update(["Work", "Daily"])
    if any("short sleeve" in a for a in attrs):
        tags.update(["Daily", "Sport", "Home"])
    if any("black" in a or "white" in a or "solid" in a for a in attrs):
        tags.add("Formal")

    if not tags:
        tags.add("Daily")

    priority = ["Daily", "Work", "Sport", "Party", "Formal", "Travel", "Home"]
    return [x for x in priority if x in tags]


def get_user_clothes(user_id: int, sort_order: str = "newest"):
    conn = get_db()
    if sort_order == "oldest":
        rows = conn.execute("""
            SELECT * FROM clothes
            WHERE user_id = ?
            ORDER BY created_at ASC, id ASC
        """, (user_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM clothes
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
        """, (user_id,)).fetchall()
    conn.close()
    return rows


def clothes_row_to_dict(row):
    keys = row.keys()
    return {
        "id": row["id"],
        "filename": row["filename"],
        "image_url": row["image_relpath"],
        "category_name": row["category_name"],
        "category_conf": row["category_conf"],
        "main_category": row["main_category"],
        "season": row["season"],
        "thickness": row["thickness"],
        "created_at": row["created_at"],
        "attribute_names": json.loads(row["attributes_json"]) if row["attributes_json"] else [],
        "occasion_tags": json.loads(row["occasion_tags_json"]) if "occasion_tags_json" in keys and row["occasion_tags_json"] else [],
        "role": row["role"] if "role" in keys else None
    }


def save_cloth_record(user_id, filename, image_relpath, feature_relpath, result):
    occasion_tags = infer_occasion_tags(
        result["category_name"],
        result["main_category"],
        result["attribute_names"]
    )
    role = infer_role(
        result["category_name"],
        result["main_category"],
        result["attribute_names"]
    )

    conn = get_db()
    cur = conn.execute("""
        INSERT INTO clothes (
            user_id, filename, image_relpath, feature_relpath,
            category_name, category_conf, main_category,
            season, thickness, attributes_json, occasion_tags_json, role
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        filename,
        image_relpath,
        feature_relpath,
        result["category_name"],
        result["category_conf"],
        result["main_category"],
        result["season"],
        result["thickness"],
        json.dumps(result["attribute_names"], ensure_ascii=False),
        json.dumps(occasion_tags, ensure_ascii=False),
        role
    ))
    conn.commit()
    cloth_id = cur.lastrowid
    conn.close()
    return cloth_id


def move_to_deleted_table(row):
    conn = get_db()
    keys = row.keys()
    conn.execute("""
        INSERT INTO deleted_clothes (
            original_cloth_id, user_id, filename, image_relpath, feature_relpath,
            category_name, category_conf, main_category, season, thickness,
            attributes_json, occasion_tags_json, role
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["id"],
        row["user_id"],
        row["filename"],
        row["image_relpath"],
        row["feature_relpath"],
        row["category_name"],
        row["category_conf"],
        row["main_category"],
        row["season"],
        row["thickness"],
        row["attributes_json"],
        row["occasion_tags_json"] if "occasion_tags_json" in keys else None,
        row["role"] if "role" in keys else None
    ))
    conn.commit()
    conn.close()