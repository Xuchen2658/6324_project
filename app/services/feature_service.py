import numpy as np

from app.config.settings import BASE_DIR
from app.services.clothes_service import clothes_row_to_dict, get_user_clothes
from app.utils.constants import TOP_K_SIMILAR


def normalize_feature(vec: np.ndarray) -> np.ndarray:
    vec = vec.astype(np.float32).reshape(-1)
    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = normalize_feature(a)
    b = normalize_feature(b)
    return float(np.dot(a, b))


def find_similar_in_user_wardrobe(user_id: int, query_feature: np.ndarray, top_k: int = TOP_K_SIMILAR):
    rows = get_user_clothes(user_id)
    results = []

    for row in rows:
        feature_path = BASE_DIR / row["feature_relpath"].lstrip("/")
        if not feature_path.exists():
            continue

        try:
            db_feat = np.load(feature_path)
            score = cosine_similarity(query_feature, db_feat)
            item = clothes_row_to_dict(row)
            item["score"] = round(score, 4)
            results.append(item)
        except Exception as e:
            print(f"⚠️ 相似检索失败: {e}")

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]