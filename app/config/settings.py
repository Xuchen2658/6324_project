from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_ANNO_PATH = BASE_DIR / "dataset" / "Anno_coarse"

# 旧模型：负责大类/主类别/特征
LEGACY_MODEL_WEIGHTS = BASE_DIR / "checkpoint_c2_full_1000.pth"

# 新模型：负责颜色 + 属性
ATTR_MODEL_WEIGHTS = BASE_DIR / "model0405.pth"
YOLO_WEIGHTS = BASE_DIR / "yolov8n-seg.pt"

CATEGORY_LIST_PATH = DATA_ANNO_PATH / "list_category_cloth.txt"
ATTR_LIST_PATH = DATA_ANNO_PATH / "list_attr_cloth.txt"

UPLOAD_DIR = BASE_DIR / "static" / "uploads"
DB_PATH = BASE_DIR / "app.db"

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