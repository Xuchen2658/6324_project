from flask import jsonify, request

from app.core.auth import current_language, current_user_id, current_username, login_required


def register_user_api_routes(app):
    @app.route("/api/language", methods=["GET", "POST"])
    @login_required
    def api_language():
        if request.method == "GET":
            return jsonify({"language": current_language()})

        data = request.get_json(silent=True) or {}
        language = data.get("language", "zh")
        if language not in {"zh", "en", "es", "ja", "ko"}:
            return jsonify({"error": "unsupported language"}), 400

        from flask import session
        session["language"] = language
        return jsonify({"language": language})

    @app.route("/api/me")
    @login_required
    def api_me():
        return jsonify({
            "user_id": current_user_id(),
            "username": current_username(),
            "language": current_language()
        })