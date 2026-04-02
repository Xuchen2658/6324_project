from functools import wraps

from flask import redirect, session, url_for

from app.utils.i18n import I18N


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return func(*args, **kwargs)
    return wrapper


def current_user_id():
    return session.get("user_id")


def current_username():
    return session.get("username")


def current_language():
    return session.get("language", "zh")


def current_messages():
    return I18N.get(current_language(), I18N["zh"])