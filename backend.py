import json
import sqlite3
import uuid
from functools import wraps
from pathlib import Path

import numpy as np
import requests
import torch
import torch.nn as nn
from flask import (
    Flask, request, jsonify, render_template,
    send_from_directory, session, redirect, url_for
)
from flask_cors import CORS
from PIL import Image
from torchvision import models, transforms
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "change_this_to_a_random_secret_key"
CORS(app)

# ================= 1. 基础配置 =================
BASE_DIR = Path(__file__).resolve().parent
DATA_ANNO_PATH = BASE_DIR / "dataset" / "Anno_coarse"
MODEL_WEIGHTS = BASE_DIR / "checkpoint_c2_full_1000.pth"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "app.db"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
TOP_K_ATTRIBUTES = 10
TOP_K_SIMILAR = 5

CITY_OPTIONS = [
    "Arlington", "Dallas", "Fort Worth", "Austin", "Houston", "San Antonio",
    "Plano", "Irving", "Richardson", "Frisco",
    "New York", "Los Angeles", "Chicago", "Seattle", "San Francisco",
    "Boston", "Washington", "Miami", "Atlanta", "Denver", "Phoenix", "Las Vegas",
    "Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Chengdu",
    "Tokyo", "Osaka", "Seoul", "Busan", "Singapore",
    "London", "Paris", "Berlin", "Madrid", "Barcelona", "Rome", "Amsterdam",
    "Toronto", "Vancouver", "Sydney", "Melbourne"
]

I18N = {
    "zh": {
        "current_user": "当前用户",
        "view_wardrobe": "查看衣橱库",
        "logout": "退出",
        "today_weather": "今日天气",
        "refresh_weather": "刷新天气",
        "city": "城市",
        "temperature": "当前温度",
        "feels_like": "体感温度",
        "temp_max": "最高温度",
        "temp_min": "最低温度",
        "rain_prob": "降雨概率",
        "no_weather": "未获取到天气信息",
        "today_recommended_clothes": "今日适合穿的衣服",
        "score": "匹配分数",
        "no_today_recommendation": "当前衣橱库暂无今日推荐",
        "search_by_category": "按类别搜索衣服",
        "search_placeholder": "输入类别，例如 hoodie / shirt / skirt",
        "search": "搜索",
        "find_similar": "找相似",
        "find_similar_desc": "上传图片不入库，只在当前账号已有衣橱库中搜索最相似衣物。",
        "search_only": "找相似",
        "no_search_result": "没有找到该类别衣物",
        "store_upload": "入库上传",
        "store_upload_desc": "上传后保存到当前账号衣橱库，并参与后续相似检索。",
        "upload_and_store": "上传并入库",
        "recognition_result": "识别结果",
        "category": "类别",
        "confidence": "置信度",
        "season": "季节",
        "thickness": "厚度",
        "most_similar_after_store": "入库后最相似衣物",
        "similarity": "相似度",
        "query_recognition": "查询图识别结果",
        "wardrobe_similar_items": "库内相似衣物",
        "no_similar_in_wardrobe": "当前衣橱库为空，或没有可比较的衣物。",
        "login": "登录",
        "register": "注册",
        "username": "用户名",
        "password": "密码",
        "invalid_credentials": "用户名或密码错误",
        "user_exists": "用户名已存在",
        "empty_credentials": "用户名和密码不能为空",
        "my_wardrobe": "我的衣橱库",
        "back_home": "返回主页",
        "delete": "删除",
        "delete_confirm": "确定删除这件衣物吗？",
        "delete_success": "删除成功",
        "item_not_found": "未找到该衣物",
        "supported_types": "支持 jpg / jpeg / png / bmp / webp",
        "clear": "清空",
        "total_items": "当前显示数量",
        "search_hint": "可按类别关键字搜索当前账号衣橱中的衣物。",
        "empty_wardrobe": "当前衣橱库为空，或没有符合筛选条件的衣物。",
        "filename": "文件名",
        "sortNewest": "按最新时间排序",
        "sortOldest": "按最早时间排序",
        "categoryFilter": "分类筛选",
        "allCategories": "全部分类",
        "mainCategory": "主分类",
        "addedTime": "入库时间",
        "batchUpload": "批量上传",
        "batchDelete": "批量删除",
        "selectAll": "全选当前页",
        "unselectAll": "取消全选",
        "selectedCount": "已选数量",
        "batchDeleteConfirm": "确定批量删除这些衣物吗？",
        "batchDeleteFail": "批量删除失败",
        "batchUploadDone": "批量上传完成",
        "recentDeleted": "最近删除",
        "restore": "恢复",
        "restoreConfirm": "确定恢复这件衣物吗？",
        "restoreSuccess": "恢复成功",
        "recentDeletedEmpty": "最近删除为空"
    },
    "en": {
        "current_user": "Current User",
        "view_wardrobe": "View Wardrobe",
        "logout": "Logout",
        "today_weather": "Today's Weather",
        "refresh_weather": "Refresh Weather",
        "city": "City",
        "temperature": "Temperature",
        "feels_like": "Feels Like",
        "temp_max": "Max Temperature",
        "temp_min": "Min Temperature",
        "rain_prob": "Rain Probability",
        "no_weather": "Weather unavailable",
        "today_recommended_clothes": "Today's Recommended Clothes",
        "score": "Score",
        "no_today_recommendation": "No recommended clothes for today",
        "search_by_category": "Search Clothes by Category",
        "search_placeholder": "Enter category, e.g. hoodie / shirt / skirt",
        "search": "Search",
        "find_similar": "Find Similar",
        "find_similar_desc": "Upload an image without storing it, and search the most similar items in the current wardrobe.",
        "search_only": "Find Similar",
        "no_search_result": "No clothes found in this category",
        "store_upload": "Store Upload",
        "store_upload_desc": "Upload and save to current user wardrobe for future similarity search.",
        "upload_and_store": "Upload and Store",
        "recognition_result": "Recognition Result",
        "category": "Category",
        "confidence": "Confidence",
        "season": "Season",
        "thickness": "Thickness",
        "most_similar_after_store": "Most Similar After Storing",
        "similarity": "Similarity",
        "query_recognition": "Query Recognition",
        "wardrobe_similar_items": "Similar Items in Wardrobe",
        "no_similar_in_wardrobe": "Wardrobe is empty or no comparable items found.",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "invalid_credentials": "Invalid username or password",
        "user_exists": "Username already exists",
        "empty_credentials": "Username and password cannot be empty",
        "my_wardrobe": "My Wardrobe",
        "back_home": "Back Home",
        "delete": "Delete",
        "delete_confirm": "Are you sure to delete this item?",
        "delete_success": "Deleted successfully",
        "item_not_found": "Item not found",
        "supported_types": "Supports jpg / jpeg / png / bmp / webp",
        "clear": "Clear",
        "total_items": "Displayed Items",
        "search_hint": "Search clothes in the current account wardrobe by category keywords.",
        "empty_wardrobe": "The wardrobe is empty or no items match the filters.",
        "filename": "Filename",
        "sortNewest": "Sort by newest",
        "sortOldest": "Sort by oldest",
        "categoryFilter": "Category Filter",
        "allCategories": "All Categories",
        "mainCategory": "Main Category",
        "addedTime": "Added Time",
        "batchUpload": "Batch Upload",
        "batchDelete": "Batch Delete",
        "selectAll": "Select All",
        "unselectAll": "Unselect All",
        "selectedCount": "Selected",
        "batchDeleteConfirm": "Are you sure to batch delete these clothes?",
        "batchDeleteFail": "Batch delete failed",
        "batchUploadDone": "Batch upload finished",
        "recentDeleted": "Recently Deleted",
        "restore": "Restore",
        "restoreConfirm": "Are you sure to restore this item?",
        "restoreSuccess": "Restore success",
        "recentDeletedEmpty": "No recently deleted items"
    },
    "es": {
        "current_user": "Usuario actual",
        "view_wardrobe": "Ver armario",
        "logout": "Cerrar sesión",
        "today_weather": "Clima de hoy",
        "refresh_weather": "Actualizar clima",
        "city": "Ciudad",
        "temperature": "Temperatura",
        "feels_like": "Sensación térmica",
        "temp_max": "Temperatura máxima",
        "temp_min": "Temperatura mínima",
        "rain_prob": "Probabilidad de lluvia",
        "no_weather": "No hay información meteorológica",
        "today_recommended_clothes": "Ropa recomendada para hoy",
        "score": "Puntuación",
        "no_today_recommendation": "No hay ropa recomendada para hoy",
        "search_by_category": "Buscar ropa por categoría",
        "search_placeholder": "Introduce una categoría, por ejemplo hoodie / shirt / skirt",
        "search": "Buscar",
        "find_similar": "Buscar similares",
        "find_similar_desc": "Sube una imagen sin guardarla y busca las prendas más similares en el armario actual.",
        "search_only": "Buscar similares",
        "no_search_result": "No se encontró ropa de esta categoría",
        "store_upload": "Subir al armario",
        "store_upload_desc": "La imagen se guardará en el armario del usuario actual y participará en búsquedas futuras.",
        "upload_and_store": "Subir y guardar",
        "recognition_result": "Resultado del reconocimiento",
        "category": "Categoría",
        "confidence": "Confianza",
        "season": "Temporada",
        "thickness": "Grosor",
        "most_similar_after_store": "Prendas más similares después de guardar",
        "similarity": "Similitud",
        "query_recognition": "Resultado de la imagen consultada",
        "wardrobe_similar_items": "Prendas similares en el armario",
        "no_similar_in_wardrobe": "El armario está vacío o no hay prendas comparables.",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "username": "Nombre de usuario",
        "password": "Contraseña",
        "invalid_credentials": "Nombre de usuario o contraseña incorrectos",
        "user_exists": "El nombre de usuario ya existe",
        "empty_credentials": "El nombre de usuario y la contraseña no pueden estar vacíos",
        "my_wardrobe": "Mi armario",
        "back_home": "Volver al inicio",
        "delete": "Eliminar",
        "delete_confirm": "¿Seguro que deseas eliminar esta prenda?",
        "delete_success": "Eliminado correctamente",
        "item_not_found": "Prenda no encontrada",
        "supported_types": "Admite jpg / jpeg / png / bmp / webp",
        "clear": "Limpiar",
        "total_items": "Cantidad mostrada",
        "search_hint": "Puedes buscar prendas del usuario actual por palabras clave de categoría.",
        "empty_wardrobe": "El armario está vacío o no hay prendas que coincidan con los filtros.",
        "filename": "Nombre de archivo",
        "sortNewest": "Ordenar por más reciente",
        "sortOldest": "Ordenar por más antiguo",
        "categoryFilter": "Filtro por categoría",
        "allCategories": "Todas las categorías",
        "mainCategory": "Categoría principal",
        "addedTime": "Fecha de ingreso",
        "batchUpload": "Carga múltiple",
        "batchDelete": "Eliminar en lote",
        "selectAll": "Seleccionar todo",
        "unselectAll": "Cancelar selección",
        "selectedCount": "Seleccionados",
        "batchDeleteConfirm": "¿Seguro que deseas eliminar estas prendas?",
        "batchDeleteFail": "Error al eliminar en lote",
        "batchUploadDone": "Carga múltiple finalizada",
        "recentDeleted": "Eliminados recientemente",
        "restore": "Restaurar",
        "restoreConfirm": "¿Seguro que deseas restaurar esta prenda?",
        "restoreSuccess": "Restaurado correctamente",
        "recentDeletedEmpty": "No hay elementos eliminados recientemente"
    },
    "ja": {
        "current_user": "現在のユーザー",
        "view_wardrobe": "クローゼットを見る",
        "logout": "ログアウト",
        "today_weather": "今日の天気",
        "refresh_weather": "天気を更新",
        "city": "都市",
        "temperature": "現在の気温",
        "feels_like": "体感温度",
        "temp_max": "最高気温",
        "temp_min": "最低気温",
        "rain_prob": "降水確率",
        "no_weather": "天気情報が取得できません",
        "today_recommended_clothes": "今日おすすめの服",
        "score": "スコア",
        "no_today_recommendation": "今日のおすすめ衣類はありません",
        "search_by_category": "カテゴリで服を検索",
        "search_placeholder": "カテゴリを入力してください。例：hoodie / shirt / skirt",
        "search": "検索",
        "find_similar": "類似を探す",
        "find_similar_desc": "画像を保存せずにアップロードし、現在のクローゼット内で最も似た服を検索します。",
        "search_only": "類似を探す",
        "no_search_result": "このカテゴリの服は見つかりませんでした",
        "store_upload": "クローゼットに保存",
        "store_upload_desc": "アップロード後、現在のアカウントのクローゼットに保存され、今後の類似検索に使用されます。",
        "upload_and_store": "アップロードして保存",
        "recognition_result": "認識結果",
        "category": "カテゴリ",
        "confidence": "信頼度",
        "season": "季節",
        "thickness": "厚さ",
        "most_similar_after_store": "保存後に最も類似した服",
        "similarity": "類似度",
        "query_recognition": "検索画像の認識結果",
        "wardrobe_similar_items": "クローゼット内の類似服",
        "no_similar_in_wardrobe": "クローゼットが空か、比較できる服がありません。",
        "login": "ログイン",
        "register": "登録",
        "username": "ユーザー名",
        "password": "パスワード",
        "invalid_credentials": "ユーザー名またはパスワードが正しくありません",
        "user_exists": "このユーザー名はすでに存在します",
        "empty_credentials": "ユーザー名とパスワードは空にできません",
        "my_wardrobe": "マイクローゼット",
        "back_home": "ホームに戻る",
        "delete": "削除",
        "delete_confirm": "この服を削除してもよろしいですか？",
        "delete_success": "削除しました",
        "item_not_found": "服が見つかりません",
        "supported_types": "jpg / jpeg / png / bmp / webp に対応",
        "clear": "クリア",
        "total_items": "表示件数",
        "search_hint": "現在のアカウントのクローゼット内の服をカテゴリキーワードで検索できます。",
        "empty_wardrobe": "クローゼットが空か、フィルター条件に一致する服がありません。",
        "filename": "ファイル名",
        "sortNewest": "新しい順",
        "sortOldest": "古い順",
        "categoryFilter": "カテゴリフィルター",
        "allCategories": "すべてのカテゴリ",
        "mainCategory": "主分類",
        "addedTime": "追加日時",
        "batchUpload": "一括アップロード",
        "batchDelete": "一括削除",
        "selectAll": "すべて選択",
        "unselectAll": "選択解除",
        "selectedCount": "選択数",
        "batchDeleteConfirm": "これらの服を一括削除してもよろしいですか？",
        "batchDeleteFail": "一括削除に失敗しました",
        "batchUploadDone": "一括アップロードが完了しました",
        "recentDeleted": "最近削除したアイテム",
        "restore": "復元",
        "restoreConfirm": "この服を復元してもよろしいですか？",
        "restoreSuccess": "復元しました",
        "recentDeletedEmpty": "最近削除したアイテムはありません"
    },
    "ko": {
        "current_user": "현재 사용자",
        "view_wardrobe": "옷장 보기",
        "logout": "로그아웃",
        "today_weather": "오늘의 날씨",
        "refresh_weather": "날씨 새로고침",
        "city": "도시",
        "temperature": "현재 기온",
        "feels_like": "체감 온도",
        "temp_max": "최고 기온",
        "temp_min": "최저 기온",
        "rain_prob": "강수 확률",
        "no_weather": "날씨 정보를 불러올 수 없습니다",
        "today_recommended_clothes": "오늘 입기 좋은 옷",
        "score": "점수",
        "no_today_recommendation": "오늘 추천할 옷이 없습니다",
        "search_by_category": "카테고리로 옷 검색",
        "search_placeholder": "카테고리를 입력하세요. 예: hoodie / shirt / skirt",
        "search": "검색",
        "find_similar": "유사 항목 찾기",
        "find_similar_desc": "이미지를 저장하지 않고 업로드하여 현재 옷장에서 가장 비슷한 옷을 찾습니다.",
        "search_only": "유사 항목 찾기",
        "no_search_result": "해당 카테고리의 옷을 찾지 못했습니다",
        "store_upload": "옷장에 저장",
        "store_upload_desc": "업로드한 이미지는 현재 계정의 옷장에 저장되며 이후 유사 검색에 사용됩니다.",
        "upload_and_store": "업로드 후 저장",
        "recognition_result": "인식 결과",
        "category": "카테고리",
        "confidence": "신뢰도",
        "season": "계절",
        "thickness": "두께",
        "most_similar_after_store": "저장 후 가장 유사한 옷",
        "similarity": "유사도",
        "query_recognition": "조회 이미지 인식 결과",
        "wardrobe_similar_items": "옷장 내 유사한 옷",
        "no_similar_in_wardrobe": "옷장이 비어 있거나 비교 가능한 옷이 없습니다.",
        "login": "로그인",
        "register": "회원가입",
        "username": "사용자 이름",
        "password": "비밀번호",
        "invalid_credentials": "사용자 이름 또는 비밀번호가 올바르지 않습니다",
        "user_exists": "이미 존재하는 사용자 이름입니다",
        "empty_credentials": "사용자 이름과 비밀번호를 입력해야 합니다",
        "my_wardrobe": "내 옷장",
        "back_home": "홈으로 돌아가기",
        "delete": "삭제",
        "delete_confirm": "이 옷을 삭제하시겠습니까?",
        "delete_success": "삭제되었습니다",
        "item_not_found": "옷을 찾을 수 없습니다",
        "supported_types": "jpg / jpeg / png / bmp / webp 지원",
        "clear": "지우기",
        "total_items": "표시된 개수",
        "search_hint": "현재 계정의 옷장에서 카테고리 키워드로 검색할 수 있습니다.",
        "empty_wardrobe": "옷장이 비어 있거나 필터 조건에 맞는 옷이 없습니다.",
        "filename": "파일명",
        "sortNewest": "최신순 정렬",
        "sortOldest": "오래된순 정렬",
        "categoryFilter": "카테고리 필터",
        "allCategories": "전체 카테고리",
        "mainCategory": "주 카테고리",
        "addedTime": "추가 시간",
        "batchUpload": "일괄 업로드",
        "batchDelete": "일괄 삭제",
        "selectAll": "전체 선택",
        "unselectAll": "전체 해제",
        "selectedCount": "선택됨",
        "batchDeleteConfirm": "이 옷들을 일괄 삭제하시겠습니까?",
        "batchDeleteFail": "일괄 삭제 실패",
        "batchUploadDone": "일괄 업로드 완료",
        "recentDeleted": "최근 삭제",
        "restore": "복원",
        "restoreConfirm": "이 옷을 복원하시겠습니까?",
        "restoreSuccess": "복원되었습니다",
        "recentDeletedEmpty": "최근 삭제한 항목이 없습니다"
    }
}

# ================= 2. 数据库 =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            image_relpath TEXT NOT NULL,
            feature_relpath TEXT NOT NULL,
            category_name TEXT,
            category_conf TEXT,
            main_category TEXT,
            season TEXT,
            thickness TEXT,
            attributes_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deleted_clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_cloth_id INTEGER,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            image_relpath TEXT NOT NULL,
            feature_relpath TEXT NOT NULL,
            category_name TEXT,
            category_conf TEXT,
            main_category TEXT,
            season TEXT,
            thickness TEXT,
            attributes_json TEXT,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_db()

# ================= 3. 登录与语言 =================
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

# ================= 4. 标签加载 =================
def load_labels():
    try:
        cat_file = DATA_ANNO_PATH / "list_category_cloth.txt"
        attr_file = DATA_ANNO_PATH / "list_attr_cloth.txt"

        with open(cat_file, "r", encoding="utf-8") as f:
            cats = [line.split()[0] for line in f.readlines()[2:]]

        with open(attr_file, "r", encoding="utf-8") as f:
            attrs = [line.strip().rsplit(None, 1)[0] for line in f.readlines()[2:]]

        return cats, attrs
    except Exception as e:
        print(f"❌ 标签文件加载失败: {e}")
        return ["Unknown"] * 50, ["Unknown"] * 1000


CATEGORY_NAMES, ATTRIBUTE_NAMES = load_labels()

# ================= 5. 模型 =================
class MultiTaskResNet(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = models.resnet50(weights=None)
        self.backbone = nn.Sequential(*(list(resnet.children())[:-1]))
        self.cat_head = nn.Linear(2048, 50)
        self.attr_head = nn.Linear(2048, 1000)

    def forward(self, x):
        feat = self.backbone(x).view(x.size(0), -1)
        return self.cat_head(feat), self.attr_head(feat), feat


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MultiTaskResNet().to(device)

if MODEL_WEIGHTS.exists():
    checkpoint = torch.load(MODEL_WEIGHTS, map_location=device)
    state_dict = checkpoint["model"] if isinstance(checkpoint, dict) and "model" in checkpoint else checkpoint
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print(f"✅ 成功加载权重: {MODEL_WEIGHTS} (使用设备: {device})")
else:
    print(f"⚠️ 未找到权重文件: {MODEL_WEIGHTS}")

# ================= 6. 工具函数 =================
def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])


def normalize_feature(vec: np.ndarray) -> np.ndarray:
    vec = vec.astype(np.float32).reshape(-1)
    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm


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


def build_user_dirs(user_id: int):
    user_root = UPLOAD_DIR / str(user_id)
    wardrobe_img_dir = user_root / "wardrobe_images"
    wardrobe_feat_dir = user_root / "wardrobe_features"
    temp_dir = user_root / "temp_queries"

    wardrobe_img_dir.mkdir(parents=True, exist_ok=True)
    wardrobe_feat_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    return wardrobe_img_dir, wardrobe_feat_dir, temp_dir


def extract_prediction_and_feature(image_path: Path):
    transform = get_transform()
    img = Image.open(image_path).convert("RGB")
    input_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        cat_logits, attr_logits, feat = model(input_tensor)

        cat_probs = torch.softmax(cat_logits, dim=1).squeeze()
        cat_idx = torch.argmax(cat_probs).item()

        attr_probs = torch.sigmoid(attr_logits).squeeze()
        topk = torch.topk(attr_probs, k=min(TOP_K_ATTRIBUTES, attr_probs.shape[0]))
        attr_indices = topk.indices.tolist()

    feature = feat.cpu().numpy().reshape(-1).astype(np.float32)
    category_name = CATEGORY_NAMES[cat_idx] if cat_idx < len(CATEGORY_NAMES) else "Unknown"
    category_conf = f"{cat_probs[cat_idx].item():.2%}"
    attribute_names = [ATTRIBUTE_NAMES[i] for i in attr_indices if i < len(ATTRIBUTE_NAMES)]
    tags = infer_extra_tags(category_name, attribute_names)
    main_category = infer_main_category(category_name, attribute_names)

    return {
        "category_name": category_name,
        "category_conf": category_conf,
        "attribute_names": attribute_names,
        "main_category": main_category,
        "season": tags["season"],
        "thickness": tags["thickness"],
        "feature": feature
    }


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = normalize_feature(a)
    b = normalize_feature(b)
    return float(np.dot(a, b))


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

# ================= 7. 天气与今日推荐 =================
def get_coordinates_by_city(city_name: str):
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return None

        return {
            "name": results[0].get("name", city_name),
            "latitude": results[0]["latitude"],
            "longitude": results[0]["longitude"],
            "country": results[0].get("country", "")
        }
    except Exception as e:
        print(f"⚠️ 地理编码失败: {e}")
        return None


def get_weather_by_coordinates(latitude: float, longitude: float):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code",
            "daily": "precipitation_probability_max,temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "forecast_days": 1
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        return {
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "precipitation": current.get("precipitation"),
            "rain": current.get("rain"),
            "showers": current.get("showers"),
            "snowfall": current.get("snowfall"),
            "weather_code": current.get("weather_code"),
            "precipitation_probability_max": (
                daily.get("precipitation_probability_max", [None])[0]
                if daily.get("precipitation_probability_max") else None
            ),
            "temp_max": (
                daily.get("temperature_2m_max", [None])[0]
                if daily.get("temperature_2m_max") else None
            ),
            "temp_min": (
                daily.get("temperature_2m_min", [None])[0]
                if daily.get("temperature_2m_min") else None
            )
        }
    except Exception as e:
        print(f"⚠️ 天气获取失败: {e}")
        return None


def score_item_for_today(item: dict, weather: dict | None) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    category = (item.get("category_name") or "").lower()
    attrs = [a.lower() for a in item.get("attribute_names", [])]
    season = item.get("season", "All Season")
    thickness = item.get("thickness", "Medium")

    if not weather:
        if season == "All Season":
            score += 1
            reasons.append("适合日常天气")
        return score, reasons

    temp = weather.get("temperature")
    rain_prob = weather.get("precipitation_probability_max")

    if temp is not None:
        if temp <= 10:
            if thickness == "Thick" or season == "Autumn/Winter":
                score += 3
                reasons.append("适合低温天气")
        elif 10 < temp <= 20:
            if thickness in {"Medium", "Thick"}:
                score += 2
                reasons.append("适合偏凉天气")
        else:
            if thickness == "Thin" or season == "Spring/Summer":
                score += 3
                reasons.append("适合温暖天气")

    if rain_prob is not None and rain_prob >= 50:
        if any(k in category for k in ["coat", "jacket"]) or any("black" in a or "dark" in a for a in attrs):
            score += 2
            reasons.append("适合可能下雨的天气")

    if not reasons:
        reasons.append("基础百搭")

    return score, reasons

# ================= 8. 页面路由 =================
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
    except sqlite3.IntegrityError:
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

# ================= 9. API：语言 =================
@app.route("/api/language", methods=["GET", "POST"])
@login_required
def api_language():
    if request.method == "GET":
        return jsonify({"language": current_language()})

    data = request.get_json(silent=True) or {}
    language = data.get("language", "zh")
    if language not in {"zh", "en", "es", "ja", "ko"}:
        return jsonify({"error": "unsupported language"}), 400

    session["language"] = language
    return jsonify({"language": language})

# ================= 10. API：用户与衣橱 =================
@app.route("/api/me")
@login_required
def api_me():
    return jsonify({
        "user_id": current_user_id(),
        "username": current_username(),
        "language": current_language()
    })


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

# ================= 11. API：最近删除与恢复 =================
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
            "attribute_names": json.loads(row["attributes_json"]) if row["attributes_json"] else []
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
            season, thickness, attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        row["attributes_json"]
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

# ================= 12. API：天气与首页仪表盘 =================
@app.route("/api/dashboard")
@login_required
def api_dashboard():
    city = request.args.get("city", CITY_OPTIONS[0]).strip() or CITY_OPTIONS[0]

    location_info = get_coordinates_by_city(city)
    weather = None
    resolved_city = city

    if location_info:
        resolved_city = location_info.get("name", city)
        weather = get_weather_by_coordinates(
            location_info["latitude"],
            location_info["longitude"]
        )

    rows = get_user_clothes(current_user_id())
    items = [clothes_row_to_dict(r) for r in rows]

    ranked = []
    for item in items:
        score, reasons = score_item_for_today(item, weather)
        ranked.append({
            **item,
            "score": score,
            "reasons": reasons[:2]
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return jsonify({
        "city_options": CITY_OPTIONS,
        "city": resolved_city,
        "weather": weather,
        "today_recommendations": ranked[:5]
    })

# ================= 13. 上传：单个入库 =================
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

# ================= 14. 上传：批量入库 =================
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

# ================= 15. 上传：找相似，不入库 =================
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

# ================= 16. 静态文件 =================
@app.route("/static/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)