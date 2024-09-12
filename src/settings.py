import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


MASTER_DB_FILE_NAME = os.path.join(
    BASE_DIR, "afaq_database", "application 19-08-2024.xlsx"
)

CATEGORIES_DB_FILE_NAME = os.path.join(
    BASE_DIR, "afaq_database", "categories.xlsx"
)

VARIANTS_DB_FILE_NAME =  os.path.join(
    BASE_DIR, "afaq_database", "variant_ids_prod.xlsx"
)

CONSIGNMENTS_DIRECTORY = os.path.join(
    BASE_DIR, "afaq_database", "depot application fin 2024"
)
