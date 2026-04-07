from pathlib import Path
import uuid

import numpy as np
from flask import jsonify, request, send_from_directory

from app.config.settings import UPLOAD_DIR
from app.core.auth import current_user_id, login_required
from app.models.predictor import extract_prediction_and_feature
from app.services.clothes_service import save_cloth_record
from app.services.feature_service import find_similar_in_user_wardrobe
from app.services.file_service import allowed_file, build_user_dirs
from app.utils.constants import TOP_K_SIMILAR


def register_upload_api_routes(app):
    @app.route("/upload_store", methods=["POST"])
    @login_required
    def upload_store():
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        user_id = current_user_id()
        wardrobe_img_dir, wardrobe_feat_dir, _ = build_user_dirs(user_id)

        ext = Path(file.filename).suffix.lower()
        file_id = uuid.uuid4().hex
        image_name = f"{file_id}{ext}"
        feature_name = f"{file_id}.npy"

        image_path = wardrobe_img_dir / image_name
        feature_path = wardrobe_feat_dir / feature_name
        file.save(image_path)

        try:
            result = extract_prediction_and_feature(image_path)
            np.save(feature_path, result["feature"])

            image_relpath = f"/static/uploads/{user_id}/wardrobe_images/{image_name}"
            feature_relpath = f"/static/uploads/{user_id}/wardrobe_features/{feature_name}"

            cloth_id = save_cloth_record(
                user_id,
                image_name,
                image_relpath,
                feature_relpath,
                result
            )

            similar_items = find_similar_in_user_wardrobe(user_id, result["feature"], top_k=TOP_K_SIMILAR + 1)
            similar_items = [x for x in similar_items if x["id"] != cloth_id][:TOP_K_SIMILAR]

            return jsonify({
                "message": "stored",
                "stored_item": {
                    "id": cloth_id,
                    "filename": image_name,
                    "image_url": image_relpath,
                    "category_name": result["category_name"],
                    "category_conf": result["category_conf"],
                    "color_name": result.get("color_name"),
                    "main_category": result["main_category"],
                    "season": result["season"],
                    "thickness": result["thickness"],
                    "attribute_names": result["attribute_names"]
                },
                "similar_items": similar_items
            })

        except Exception as e:
            print(f"❌ 入库失败: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/upload_store_batch", methods=["POST"])
    @login_required
    def upload_store_batch():
        files = request.files.getlist("files")

        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        user_id = current_user_id()
        wardrobe_img_dir, wardrobe_feat_dir, _ = build_user_dirs(user_id)

        stored_items = []
        failed_items = []

        for file in files:
            try:
                if not file or file.filename == "":
                    failed_items.append({"filename": "", "error": "Empty filename"})
                    continue

                if not allowed_file(file.filename):
                    failed_items.append({"filename": file.filename, "error": "Unsupported file type"})
                    continue

                ext = Path(file.filename).suffix.lower()
                file_id = uuid.uuid4().hex
                image_name = f"{file_id}{ext}"
                feature_name = f"{file_id}.npy"

                image_path = wardrobe_img_dir / image_name
                feature_path = wardrobe_feat_dir / feature_name
                file.save(image_path)

                result = extract_prediction_and_feature(image_path)
                np.save(feature_path, result["feature"])

                image_relpath = f"/static/uploads/{user_id}/wardrobe_images/{image_name}"
                feature_relpath = f"/static/uploads/{user_id}/wardrobe_features/{feature_name}"

                cloth_id = save_cloth_record(
                    user_id,
                    image_name,
                    image_relpath,
                    feature_relpath,
                    result
                )

                stored_items.append({
                    "id": cloth_id,
                    "filename": image_name,
                    "image_url": image_relpath,
                    "category_name": result["category_name"],
                    "category_conf": result["category_conf"],
                    "color_name": result.get("color_name"),
                    "main_category": result["main_category"],
                    "season": result["season"],
                    "thickness": result["thickness"],
                    "attribute_names": result["attribute_names"]
                })

            except Exception as e:
                failed_items.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        return jsonify({
            "message": "batch upload finished",
            "stored_items": stored_items,
            "failed_items": failed_items,
            "stored_count": len(stored_items),
            "failed_count": len(failed_items)
        })

    @app.route("/search_similar", methods=["POST"])
    @login_required
    def search_similar():
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        user_id = current_user_id()
        _, _, temp_dir = build_user_dirs(user_id)

        ext = Path(file.filename).suffix.lower()
        temp_name = f"query_{uuid.uuid4().hex}{ext}"
        temp_path = temp_dir / temp_name
        file.save(temp_path)

        try:
            result = extract_prediction_and_feature(temp_path)
            similar_items = find_similar_in_user_wardrobe(user_id, result["feature"], top_k=TOP_K_SIMILAR)

            if temp_path.exists():
                temp_path.unlink()

            return jsonify({
                "query_result": {
                    "category_name": result["category_name"],
                    "category_conf": result["category_conf"],
                    "color_name": result.get("color_name"),
                    "main_category": result["main_category"],
                    "season": result["season"],
                    "thickness": result["thickness"],
                    "attribute_names": result["attribute_names"]
                },
                "similar_items": similar_items
            })

        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            print(f"❌ 相似检索失败: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/static/uploads/<path:filename>")
    def serve_uploads(filename):
        return send_from_directory(UPLOAD_DIR, filename)