from random import randint

from src.settings import (
    MASTER_DB_FILE_NAME,
    CATEGORIES_DB_FILE_NAME,
)

from src.utils import (
    handle_excel_file,
    export_xlsx,
    format_price,
    format_isbn,
)


def adapt_products():
    # Read main application data
    column_names = [
        "ID",
        "Référence",
        "Désignation",
        "Auteur",
        "Éditeur",
        "Catégorie",
        "Sous-catégorie",
        "Quantité en Stock",
        "Prix  vente1 ",
        "Prix 2",
        "Prix 3",
        "pourcentage ",
        "Prix d'achat",
        "Tva",
        "Unité de vente",
        "Unité d'achat",
        "Marque",
        "Couleur",
        "Taille",
        "Stock emplacement",
        "Seuil d'alerte",
        "Date de parution",
        "Phonétique",
        "ISBN",
        "Couverture",
    ]
    start_row = 1
    data = handle_excel_file(MASTER_DB_FILE_NAME, start_row, column_names)
    rows = data["data"]

    # Read categories data
    cat_column_names = [
        "id",
        "name",
    ]
    start_row = 1
    data = handle_excel_file(CATEGORIES_DB_FILE_NAME, start_row, cat_column_names)
    categories_db = data["data"]

    def get_category_id(name):
        try:
            return (
                lambda name: next(
                    cat["id"] for cat in categories_db if name == cat["name"]
                )
            )(name)
        except StopIteration:
            return None

    # Shared attributes
    taxes_id = "librarian.books_taxes_sale"
    supplier_taxes_id = "librarian.books_taxes_purchase"
    product_type = "Produit stockable"
    is_book = True
    available_in_pos = True

    products = []
    isbn_list = []
    product_id = 1

    for index, row in enumerate(rows):
        row_id = row["id"]
        product_ref = row["reference"]
        product_name = row["designation"]
        author_name = row["auteur"]
        editor_name = row["editeur"]
        category_name = row["categorie"]
        child_category_name = row["sous-categorie"]
        in_hand_qty = row["quantite-en-stock"]
        price = row["prix-vente1"]
        profit = row["pourcentage"]
        buy_price = row["prix-dachat"]
        size = row["taille"]
        release_date = row["date-de-parution"]
        isbn = row["isbn"]
        cover = row["couverture"]

        author_ids = row_id + ".author" if author_name else ""
        editor_id = row_id + ".editor" if editor_name else ""

        category = child_category_name if child_category_name else category_name

        # Format prices
        price = format_price(price)
        buy_price = format_price(buy_price)
        try:
            profit = float(profit.replace("%", "")) if profit else None
        except AttributeError:
            pass
        except ValueError:
            profit = None

        if buy_price and not price:
            price = buy_price

        if profit and price:
            buy_price = price - (price * profit)
        elif buy_price and price:
            profit = (price - buy_price) / buy_price

        # Format ISBN
        product_ref = format_isbn(product_ref)
        isbn = format_isbn(isbn)
        if product_ref and not isbn:
            isbn = product_ref

        if not (isbn.isdigit() and len(isbn) in [10, 13]):
            if product_ref.isdigit() and len(product_ref) in [10, 13]:
                isbn = product_ref

        if isbn:
            if isbn in isbn_list:
                isbn = isbn + f"_{randint(1000, 10000)}"
            isbn_list.append(isbn)

        # Format category
        pos_categ_ids = "librarian.product_pos_category_book"
        root_parent_category_id = "librarian.product_category_book"
        category_id = get_category_id(category)
        if not category_id:
            category_id = root_parent_category_id

        # Format cover
        cover = "paper_cover" if cover == "ورقي" else "hard_cover"

        # Fix unnamed products
        if not product_name:
            continue

        products.append(
            (
                row_id,
                isbn,
                isbn,
                product_name,
                author_ids,
                editor_id,
                category_id,
                price,
                profit * 100 if profit else profit,
                buy_price,
                size,
                release_date,
                cover,
                product_type,
                is_book,
                available_in_pos,
                pos_categ_ids,
                taxes_id,
                supplier_taxes_id,
                in_hand_qty,
            )
        )
        product_id += 1

    # Export adapted data to excel format
    export_column_names = [
        "id",
        "barcode",
        "isbn",
        "name",
        "author_ids/id",
        "editor_id/id",
        "categ_id/id",
        "list_price",
        "profit_percent",
        "standard_price",
        "size",
        "release_year",
        "cover",
        "type",
        "is_book",
        "available_in_pos",
        "pos_categ_ids/id",
        "taxes_id/id",
        "supplier_taxes_id/id",
        "quantity",
    ]
    export_data = {
        "col_titles": export_column_names,
        "data": products,
    }
    export_xlsx(
        data=export_data,
        sheet_title="Produits",
    )
