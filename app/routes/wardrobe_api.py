from flask import jsonify, request

from app.core.auth import current_messages, current_user_id, login_required
from app.core.database import get_db
from app.services.clothes_service import clothes_row_to_dict, get_user_clothes, move_to_deleted_table


def register_wardrobe_api_routes(app):
    @app.route("/api/wardrobe")
    @login_required
    def api_wardrobe():
        sort_order = request.args.get("sort", "newest")
        rows = get_user_clothes(current_user_id(), sort_order=sort_order)
        return jsonify({
            "items": [clothes_row_to_dict(r) for r in rows]
        })

    @app.route("/api/clothes/<int:cloth_id>", methods=["DELETE"])
    @login_required
    def api_delete_cloth(cloth_id):
        user_id = current_user_id()
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM clothes WHERE id = ? AND user_id = ?",
            (cloth_id, user_id)
        ).fetchone()

        if not row:
            conn.close()
            return jsonify({"error": current_messages()["item_not_found"]}), 404

        move_to_deleted_table(row)

        conn.execute("DELETE FROM clothes WHERE id = ? AND user_id = ?", (cloth_id, user_id))
        conn.commit()
        conn.close()

        return jsonify({"message": current_messages()["delete_success"]})

    @app.route("/api/clothes/batch_delete", methods=["POST"])
    @login_required
    def api_batch_delete_clothes():
        data = request.get_json(silent=True) or {}
        ids = data.get("ids", [])

        if not isinstance(ids, list) or not ids:
            return jsonify({"error": "No ids provided"}), 400

        user_id = current_user_id()
        conn = get_db()

        placeholders = ",".join(["?"] * len(ids))
        rows = conn.execute(
            f"SELECT * FROM clothes WHERE user_id = ? AND id IN ({placeholders})",
            [user_id] + ids
        ).fetchall()

        for row in rows:
            move_to_deleted_table(row)

        conn.execute(
            f"DELETE FROM clothes WHERE user_id = ? AND id IN ({placeholders})",
            [user_id] + ids
        )
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Batch delete success",
            "deleted_count": len(rows)
        })

    @app.route("/api/search_clothes")
    @login_required
    def api_search_clothes():
        q = request.args.get("q", "").strip().lower()
        if not q:
            return jsonify({"items": []})

        rows = get_user_clothes(current_user_id())
        items = [clothes_row_to_dict(r) for r in rows]

        filtered = [
            item for item in items
            if q in (item.get("category_name") or "").lower()
        ]

        return jsonify({"items": filtered})