from random import randint
import os
import re
from slugify import slugify

from src.settings import (
    BASE_DIR,
    CONSIGNMENTS_DIRECTORY,
)

from src.utils import (
    handle_excel_file,
    export_xlsx,
    format_isbn,
    get_filenames,
)


def generate_consignments_import_files():
    # Read main application data
    column_names = [
        "product_qty",
        "price_unit",
        "product_id",
        "isbn",
        "partner_id",
        "discount",
    ]
    start_row = 1
    # Params
    order_line_taxes_id = "Taxe d'achat des livres"  # order_line/taxes_id

    # Read products dataset
    products_column_names = [
        "id",
        "barcode",
        "isbn",
        "name",
    ]
    products_dataset = handle_excel_file(
        os.path.join(BASE_DIR, "export", "produits_20240913103442.xlsx"),
        start_row,
        products_column_names,
    )
    products_data = products_dataset["data"]

    def get_product_id(name, isbn):
        name = re.sub(" +", " ", str(name)).strip()
        isbn = format_isbn(isbn)
        for p in products_data:
            pname = re.sub(" +", " ", str(p["name"])).strip()
            if name == pname:
                return p["id"]
            elif isbn and isbn in (p["isbn"], p["barcode"]):
                return p["id"]
        return None

    variants_column_names = ["id", "product_variant_ids_id"]
    variants_dataset = handle_excel_file(
        os.path.join(BASE_DIR, "export", "product_product.xlsx"),
        start_row,
        variants_column_names,
    )
    variants_data = variants_dataset["data"]

    def get_variant_id(p_id):
        for v in variants_data:
            if v["id"] == p_id:
                return v["product_variant_ids_id"]
        return None

    consignment_files = get_filenames(CONSIGNMENTS_DIRECTORY, "xlsx")[1:]
    purchase_order_id_format = "__import__.purchase.order.%d"

    for consignment_file in consignment_files:
        data = handle_excel_file(consignment_file, start_row, column_names)
        rows = data["data"]

        consignment_lines = []
        is_consignment_in = True

        for index, row in enumerate(rows):
            product_qty = row["product_qty"]
            price_unit = row["price_unit"]
            product_id = row["product_id"]
            isbn = row["isbn"]
            partner_id = row["partner_id"]
            discount = row["discount"]

            consignment_lines.append(
                (
                    purchase_order_id_format.format(randint(10000, 99999)),
                    partner_id,
                    is_consignment_in,
                    get_product_id(product_id, isbn),
                    get_variant_id(get_product_id(product_id, isbn)),
                    product_id,  # order line description
                    product_qty,
                    price_unit,
                    order_line_taxes_id,
                    discount * 100 if discount else "",
                )
            )

        # Export adapted data to excel format
        export_column_names = [
            "id",
            "partner_id",
            "is_consignment_in",
            "order_line/product_id/template_id",
            "order_line/product_id/id",
            "order_line/name",
            "order_line/product_qty",
            "order_line/price_unit",
            "order_line/taxes_id",
            "order_line/discount",
        ]
        export_data = {
            "col_titles": export_column_names,
            "data": consignment_lines,
        }
        export_xlsx(
            data=export_data,
            sheet_title=slugify(consignment_file.split("/")[-1].split(".")[0]),
            tmp_file_dir=os.path.join(BASE_DIR, "export", "consignments"),
        )
