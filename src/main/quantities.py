from src.settings import (
    MASTER_DB_FILE_NAME,
    VARIANTS_DB_FILE_NAME,
)

from src.utils import (
    handle_excel_file,
    export_xlsx,
    generate_number_with_fixed_size,
)


def define_product_quantities():
    # Read main application data
    column_names = [
        "ID",
        "Quantité en Stock",
    ]
    start_row = 1
    data = handle_excel_file(MASTER_DB_FILE_NAME, start_row, column_names)
    rows = data["data"]

    # Read product_variants data
    variant_column_names = [
        "id",
        "product_variant_ids/id",
    ]
    start_row = 1
    data = handle_excel_file(VARIANTS_DB_FILE_NAME, start_row, variant_column_names)
    variants_db = data["data"]

    def get_variant_id(p_id):
        try:
            return (
                lambda p_id: next(
                    p["product_variant_idsid"] for p in variants_db if p_id == p["id"]
                )
            )(p_id)
        except StopIteration:
            return None

    products = []

    # Params
    location_id = "stock.stock_location_stock"

    for index, row in enumerate(rows):
        row_id = row["id"]
        variant_id = get_variant_id(row_id)
        if not variant_id:
            continue

        in_hand_qty = row["quantite-en-stock"]
        adjustment_id = (
            f"__import__.stock.quant.{generate_number_with_fixed_size(index + 1, 5)}"
        )

        products.append((adjustment_id, variant_id, location_id, in_hand_qty))

    # Export adapted data to excel format
    export_column_names = [
        "id",
        "product_id/id",
        "location_id/id",
        "inventory_quantity",
    ]
    export_data = {
        "col_titles": export_column_names,
        "data": products,
    }
    export_xlsx(
        data=export_data,
        sheet_title="Quantities",
    )
