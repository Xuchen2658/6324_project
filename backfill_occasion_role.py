import json

from app.core.database import get_db, init_db
from app.services.clothes_service import infer_occasion_tags, infer_role


def main():
    init_db()
    conn = get_db()
    rows = conn.execute("SELECT * FROM clothes").fetchall()

    updated = 0
    for row in rows:
        attrs = json.loads(row["attributes_json"]) if row["attributes_json"] else []

        occasion_tags = infer_occasion_tags(
            row["category_name"],
            row["main_category"],
            attrs
        )
        role = infer_role(
            row["category_name"],
            row["main_category"],
            attrs
        )

        conn.execute("""
            UPDATE clothes
            SET occasion_tags_json = ?, role = ?
            WHERE id = ?
        """, (
            json.dumps(occasion_tags, ensure_ascii=False),
            role,
            row["id"]
        ))
        updated += 1

    conn.commit()
    conn.close()
    print(f"✅ 回填完成，共更新 {updated} 条衣物数据")


if __name__ == "__main__":
    main()