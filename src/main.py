from src.settings import MASTER_DB_FILE_NAME
import json

from src.utils import (
    handle_excel_file,
    export_xlsx,
    generate_number_with_fixed_size,
    get_category
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

        # if index > 1000:
        #     break

    # Display in json format
    with open("categories.json", 'w', encoding="utf-8") as f:
        json.dump(categories, f, indent=4)

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


def main():
    adapt_product_categories()


if __name__ == "__main__":
    main()
