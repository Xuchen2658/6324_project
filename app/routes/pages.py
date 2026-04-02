from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.auth import current_language, current_messages, current_username, login_required
from app.core.database import get_db


def register_page_routes(app):
    @app.route("/")
    @login_required
    def index():
        return render_template(
            "index.html",
            username=current_username(),
            language=current_language()
        )

    @app.route("/wardrobe")
    @login_required
    def wardrobe_page():
        return render_template(
            "wardrobe.html",
            username=current_username(),
            language=current_language()
        )

    @app.route("/recent_deleted")
    @login_required
    def recent_deleted_page():
        return render_template(
            "recent_deleted.html",
            username=current_username(),
            language=current_language()
        )

    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        if request.method == "GET":
            return render_template("login.html", error=None, language=current_language(), t=current_messages())

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                error=current_messages()["invalid_credentials"],
                language=current_language(),
                t=current_messages()
            )

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        if "language" not in session:
            session["language"] = "zh"
        return redirect(url_for("index"))

    @app.route("/register", methods=["GET", "POST"])
    def register_page():
        if request.method == "GET":
            return render_template("register.html", error=None, language=current_language(), t=current_messages())

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template(
                "register.html",
                error=current_messages()["empty_credentials"],
                language=current_language(),
                t=current_messages()
            )

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            conn.commit()
        except Exception:
            conn.close()
            return render_template(
                "register.html",
                error=current_messages()["user_exists"],
                language=current_language(),
                t=current_messages()
            )

        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        if "language" not in session:
            session["language"] = "zh"

        return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login_page"))