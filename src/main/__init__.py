from .categories import adapt_product_categories
from .products import adapt_products
from .quantities import define_product_quantities
from .consignments import generate_consignments_import_files
from .sales import generate_sales


def main(operation):
    # if operation == "categories"
    match operation:
        case "categories":
            adapt_product_categories()
        case "products":
            adapt_products()
        case "quantities":
            define_product_quantities()
        case "consignments":
            generate_consignments_import_files()
        case "generate_sales":
            generate_sales()
        case _:
            print("Select a valid choice!")
