from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_ANNO_PATH = BASE_DIR / "dataset" / "Anno_coarse"
MODEL_WEIGHTS = BASE_DIR / "checkpoint_c2_full_1000.pth"
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