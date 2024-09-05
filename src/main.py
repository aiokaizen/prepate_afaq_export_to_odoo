from src.settings import MASTER_DB_FILE_NAME

from src.utils import (
    handle_excel_file,
    export_xlsx,
    generate_number_with_fixed_size,
    get_category,
    format_price,
    format_isbn
)


def adapt_product_categories():
    start_row = 1
    column_names = [
        "ID", "Catégorie", "Sous-categorie"
    ]
    data = handle_excel_file(
        MASTER_DB_FILE_NAME, start_row, column_names
    )
    rows = data["data"]

    category_external_id_format = "__import__.product_category.{cat_id}"
    categories = []
    root_parent_category_id = "librarian.product_category_book"
    category_id = 1
    for index, row in enumerate(rows):

        category = row["categorie"]
        parent_category_id = None
        child_category = row["sous-categorie"]

        if not category and not child_category:
            print("001 | ROW EMPTY")
            continue

        if category:
            if get_category(category, categories) is None:
                categories.append((
                    category_external_id_format.format(
                        cat_id=generate_number_with_fixed_size(category_id)
                    ),
                    category,
                    root_parent_category_id,
                    1
                ))
                category_id += 1
            else:
                categories = list(map(
                    lambda cat: (cat[0], cat[1], cat[2], cat[3] + 1) if cat[1] == category else cat,
                    categories
                ))
            parent_category_id = get_category(category, categories)[0]
        else:
            print("002 | CATEGORY EMPTY")

        if child_category:
            if get_category(child_category, categories) is None:
                categories.append((
                    category_external_id_format.format(
                        cat_id=generate_number_with_fixed_size(category_id)
                    ),
                    child_category,
                    parent_category_id or root_parent_category_id,
                    1
                ))
                category_id += 1
            else:
                categories = list(map(
                    lambda cat: (cat[0], cat[1], cat[2], cat[3] + 1) if cat[1] == child_category else cat,
                    categories
                ))
        else:
            print("003 | CHILD CATEGORY EMPTY")

    # Export adapted data to excel format
    export_column_names = ["id", "name", "parent_id/id"]  # , "occurrences" ]
    export_data = {
        "col_titles": export_column_names,
        "data": categories,
    }
    export_xlsx(
        data=export_data,
        sheet_title="Categories",
    )


def adapt_products():
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
    data = handle_excel_file(
        MASTER_DB_FILE_NAME, start_row, column_names
    )
    rows = data["data"]
    print("column_name:", data["column_names"])
    product_external_id_format = "__import__.product_product.{product_id}"

    products = []
    product_id = 1
    for index, row in enumerate(rows):

        # slugified_column_names = [
        #     'id', 'reference', 'designation', 'auteur', 'editeur',
        #     'categorie', 'sous-categorie', 'quantite-en-stock',
        #     'prix-vente1', 'prix-2', 'prix-3', 'pourcentage',
        #     'prix-dachat', 'tva', 'unite-de-vente', 'unite-dachat',
        #     'marque', 'couleur', 'taille', 'stock-emplacement',
        #     'seuil-dalerte', 'date-de-parution', 'phonetique',
        #     'isbn', 'couverture'
        # ]
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
        brand = row["marque"]
        size = row["taille"]
        release_date = row["date-de-parution"]
        phonetic = row["phonetique"]
        isbn = row["isbn"]
        # Possible invalid values:
        # SANS ISBN
        # sans-isbn
        # <BLANK>
        cover = row["couverture"]

        author_ids = row_id + ".author" if author_name else ""
        editor_id = row_id + ".editor" if editor_name else ""

        category = child_category_name if child_category_name else category_name

        # Format prices
        price = format_price(price)
        buy_price = format_price(buy_price)
        try:
            profit = int(profit.replace("%", '')) if profit else None
        except AttributeError:
            pass

        if buy_price and not price:
            price = buy_price

        if profit and price:
            buy_price = price - (price * profit)
        elif buy_price and price:
            profit = (price - buy_price) / buy_price * 100

        # Format ISBN
        product_ref = format_isbn(product_ref)
        isbn = format_isbn(isbn)
        if product_ref and not isbn:
            isbn = product_ref

        if not(isbn.isdigit() and len(isbn) in [10, 13]):
            if product_ref.isdigit() and len(product_ref) in [10, 13]:
                isbn = product_ref

        product_type = "Produit stockable"

        products.append((
            row_id,
            isbn,
            product_name,
            author_ids,
            editor_id,
            category,
            # in_hand_qty,
            price,
            profit,
            buy_price,
            size,
            release_date,
            cover,
            product_type
        ))
        product_id += 1

    # Export adapted data to excel format
    export_column_names = [
            "id",
            "barcode",
            "name",
            "author_ids/id",
            "editor_id/id",
            "categ_id",
            "list_price",
            "profit_percent",
            "standard_price",
            "size",
            "release_date",
            "cover",
            "type"

    ]
    export_data = {
        "col_titles": export_column_names,
        "data": products,
    }
    export_xlsx(
        data=export_data,
        sheet_title="Produits",
    )


def main():
    # adapt_product_categories()
    adapt_products()


if __name__ == "__main__":
    main()
