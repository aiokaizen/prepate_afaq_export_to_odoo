from rapidfuzz import fuzz

from src.settings import (
    MASTER_DB_FILE_NAME,
    VARIANTS_DB_FILE_NAME,
)

from src.utils import (
    handle_excel_file,
    export_xlsx,
    generate_number_with_fixed_size,
)

stopped_iterations = 0
stopped_iterations2 = 0


def get_variant_id(name, variants_db):
    global stopped_iterations
    global stopped_iterations2
    try:
        return (
            lambda name: next(
                p["product-variant-ids-id"] for p in variants_db if name == p["name"]
            )
        )(name)
    except StopIteration:
        stopped_iterations += 1
        print(f"{stopped_iterations} | Iteration stopped")
        try:
            return (
                lambda name: next(
                    p["product-variant-ids-id"]
                    for p in variants_db
                    if (
                        p["name"] != " " and fuzz.ratio(name, p["name"]) > 90
                    )  # name == p["name"])
                )
            )(name)
        except StopIteration:
            stopped_iterations2 += 1
            print(f"{stopped_iterations2} | Iteration2 stopped")
            return None


def generate_sales():
    # Call generate sale main function
    return _generate_sales()

    # Prepare data for _generate_sales()

    column_names = [
        "product",
        "quantity",
    ]
    start_row = 1
    data = handle_excel_file(
        "afaq_database/new afaq sales raw.xlsx", start_row, column_names
    )
    rows = data["data"]

    products = {}

    def product_exists(name):
        for product_name in products.keys():
            if fuzz.partial_ratio(name, product_name) > 90:
                return product_name
        return False

    for row in rows:
        product_name = row["product"]
        product_qty = row["quantity"]
        print("Name:", product_name, "\nQuantity:", product_qty)
        existing_name = product_exists(product_name)
        if not existing_name:
            products[product_name] = {
                "quantity": product_qty,
            }
        else:
            products[existing_name]["quantity"] += product_qty

    # products = sorted(products)
    final_products = []
    for name, p in products.items():
        final_products.append((name, p["quantity"]))

    # Export adapted data to excel format
    export_column_names = [
        "product",
        "quantity",
    ]
    export_data = {
        "col_titles": export_column_names,
        "data": final_products,
    }
    export_xlsx(
        data=export_data,
        sheet_title="Sale Data Preparation",
    )


def _generate_sales():
    column_names = [
        "product",
        "quantity",
    ]
    start_row = 1
    data = handle_excel_file(
        "export/sale-data-preparation_20241112185212.xlsx", start_row, column_names
    )
    rows = data["data"]

    # Read product_variants data
    variant_column_names = [
        "id",
        "name",
        "product_variant_ids/id",
    ]
    start_row = 1
    data = handle_excel_file(VARIANTS_DB_FILE_NAME, start_row, variant_column_names)
    variants_db = data["data"]

    products = []

    # Params
    sale_id = "__import__.sale_order_v2"
    name = "SS00003"
    partner_id = "__export__.res_partner_92873_as76de"
    tax_id = "librarian.books_taxes_sale"
    order_line_id_prefix = "__import__.sale_order_line_03{}"

    for index, row in enumerate(rows):
        ol_id = order_line_id_prefix.format(index + 1)
        ol_name = row["product"]
        product_id = get_variant_id(ol_name, variants_db)
        product_qty = row["quantity"]

        products.append(
            (
                sale_id,
                partner_id,
                name,
                ol_id,
                ol_name,
                product_id,
                product_qty,
                tax_id,
            )
        )

    # Export adapted data to excel format
    export_column_names = [
        "id",
        "partner_id/id",
        "name",
        "order_line/id",
        "order_line/name",
        "order_line/product_id/id",
        "order_line/product_uom_qty",
        "order_line/tax_id/id",
    ]
    export_data = {
        "col_titles": export_column_names,
        "data": products,
    }
    export_xlsx(
        data=export_data,
        sheet_title="Sales",
    )
