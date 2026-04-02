from pathlib import Path

from app.config.settings import UPLOAD_DIR
from app.utils.constants import ALLOWED_EXTENSIONS


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def build_user_dirs(user_id: int):
    user_root = UPLOAD_DIR / str(user_id)
    wardrobe_img_dir = user_root / "wardrobe_images"
    wardrobe_feat_dir = user_root / "wardrobe_features"
    temp_dir = user_root / "temp_queries"

    wardrobe_img_dir.mkdir(parents=True, exist_ok=True)
    wardrobe_feat_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    return wardrobe_img_dir, wardrobe_feat_dir, temp_dir