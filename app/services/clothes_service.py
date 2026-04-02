import json

from app.core.database import get_db


def infer_main_category(category_name: str, attribute_names: list[str]) -> str:
    cat = (category_name or "").lower()
    attrs = [a.lower() for a in attribute_names]

    if any(k in cat for k in ["shoe", "sneaker", "boot", "heel", "sandal"]):
        return "Shoes"
    if any(k in cat for k in ["hat", "cap", "beanie"]):
        return "Hats"
    if any(k in cat for k in ["skirt", "dress"]):
        return "Skirts"
    if any(k in cat for k in ["pant", "jean", "trouser", "shorts", "legging"]):
        return "Pants"
    if any(k in cat for k in ["sweater", "knit", "cardigan"]):
        return "Sweaters"
    if any(k in cat for k in ["coat", "jacket", "hoodie", "outerwear"]):
        return "Outerwear"
    if any("short" in a and "sleeve" in a for a in attrs):
        return "Short Sleeve"
    if any("long" in a and "sleeve" in a for a in attrs):
        return "Long Sleeve"
    if any(k in cat for k in ["shirt", "top", "blouse", "tee", "t-shirt", "tank"]):
        return "Tops"

    return "Others"


def infer_extra_tags(category_name: str, attribute_names: list[str]) -> dict:
    cat = category_name.lower()
    attrs = [a.lower() for a in attribute_names]

    season = "All Season"
    thickness = "Medium"

    if any(k in cat for k in ["coat", "jacket", "sweater", "hoodie"]):
        season = "Autumn/Winter"
        thickness = "Thick"
    elif any(k in cat for k in ["t-shirt", "tee", "tank", "shorts"]):
        season = "Spring/Summer"
        thickness = "Thin"

    if any("long" in a and "sleeve" in a for a in attrs):
        thickness = "Medium"

    return {
        "season": season,
        "thickness": thickness
    }


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
        "attribute_names": json.loads(row["attributes_json"]) if row["attributes_json"] else []
    }


def save_cloth_record(user_id, filename, image_relpath, feature_relpath, result):
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO clothes (
            user_id, filename, image_relpath, feature_relpath,
            category_name, category_conf, main_category,
            season, thickness, attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        json.dumps(result["attribute_names"], ensure_ascii=False)
    ))
    conn.commit()
    cloth_id = cur.lastrowid
    conn.close()
    return cloth_id


def move_to_deleted_table(row):
    conn = get_db()
    conn.execute("""
        INSERT INTO deleted_clothes (
            original_cloth_id, user_id, filename, image_relpath, feature_relpath,
            category_name, category_conf, main_category, season, thickness,
            attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        row["attributes_json"]
    ))
    conn.commit()
    conn.close()