import sys

from src.main import main
from src.settings import VALID_OPERATIONS


if __name__ == "__main__":
    available_arguments = set(["start", "help"])

    if not available_arguments.intersection(sys.argv):
        print(
            "ERROR :  Invalid arguments for manage.py. Please specify at least one of the following operations:"
            "\n\t> help   : Display a help message"
            "\n\t> start  : Start the main program\n"
        )
        exit()

    if "help" in sys.argv:
        print(
            "\nUsage: python manage.py command [options]"
            "\n\nAvailable commands:"
            "\n\t> start   : Start the main program"
            "\n\t  --demo  : Limit total data to only a small subset."
            "\n\t  --limit-rows  : Limit total rows of an excel file to the provided number."
            "\n\t> help   : Display this help message"
            "\n\t  --doc  : Show the documentation.\n"
        )
        exit()

    elif "start" in sys.argv:
        try:
            operation = sys.argv[2]
            if operation not in VALID_OPERATIONS:
                print(
                    """Invalid operation! Please choose from the list below:
        - categories
        - products
        - quantities
        - consignments
        - generate_sales
                """
                )
        except Exception:
            print(
                """Please provide an operation!
    Choices:
        - categories
        - products
        - quantities
        - consignments
        - generate_sales
"""
            )
            exit()

        main(operation)
