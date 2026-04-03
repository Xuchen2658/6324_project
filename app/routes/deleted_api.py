import json

from flask import jsonify

from app.core.auth import current_user_id, login_required
from app.core.database import get_db


def register_deleted_api_routes(app):
    @app.route("/api/recent_deleted")
    @login_required
    def api_recent_deleted():
        user_id = current_user_id()
        conn = get_db()
        rows = conn.execute("""
            SELECT * FROM deleted_clothes
            WHERE user_id = ?
            ORDER BY deleted_at DESC, id DESC
            LIMIT 50
        """, (user_id,)).fetchall()
        conn.close()

        items = []
        for row in rows:
            items.append({
                "id": row["id"],
                "original_cloth_id": row["original_cloth_id"],
                "filename": row["filename"],
                "image_url": row["image_relpath"],
                "category_name": row["category_name"],
                "category_conf": row["category_conf"],
                "main_category": row["main_category"],
                "season": row["season"],
                "thickness": row["thickness"],
                "deleted_at": row["deleted_at"],
                "attribute_names": json.loads(row["attributes_json"]) if row["attributes_json"] else [],
                "occasion_tags": json.loads(row["occasion_tags_json"]) if row["occasion_tags_json"] else [],
                "role": row["role"]
            })

        return jsonify({"items": items})

    @app.route("/api/recent_deleted/<int:deleted_id>/restore", methods=["POST"])
    @login_required
    def api_restore_deleted_cloth(deleted_id):
        user_id = current_user_id()
        conn = get_db()

        row = conn.execute("""
            SELECT * FROM deleted_clothes
            WHERE id = ? AND user_id = ?
        """, (deleted_id, user_id)).fetchone()

        if not row:
            conn.close()
            return jsonify({"error": "Deleted item not found"}), 404

        cur = conn.execute("""
            INSERT INTO clothes (
                user_id, filename, image_relpath, feature_relpath,
                category_name, category_conf, main_category,
                season, thickness, attributes_json, occasion_tags_json, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
            row["occasion_tags_json"],
            row["role"]
        ))

        restored_id = cur.lastrowid

        conn.execute("""
            DELETE FROM deleted_clothes
            WHERE id = ? AND user_id = ?
        """, (deleted_id, user_id))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Restore success",
            "restored_id": restored_id
        })