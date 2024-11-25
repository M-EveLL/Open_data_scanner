"""Parses open data on Canada's Open Government Portal, to provide the 
user with a complete inventory of datasets and resources in csv files.
"""

import atexit
from typing import List, NoReturn
import warnings
from colorama import Fore

from .constants import REGISTRY_BASE_URL
from .tools import RequestsDataCatalogue
from .inventories import Inventory


warnings.filterwarnings('ignore', category=FutureWarning)


@atexit.register
def display_exit_message() -> NoReturn:
    """Closes WebDriver(s) and asks user to click enter when program ends, so 
    user has time to read all logged messages if needed before closing 
    console.
    """
    print(Fore.CYAN + '\nClick Enter to exit.' + Fore.RESET)
    input()


def main() -> NoReturn:
    """Main code."""

    print()
    print(Fore.YELLOW + '\tOpen Data Portal Scanner' + Fore.RESET)

    # Prompt the user for department input or selection
    print('\nReady to scan information from the Open Data Portal (Registry).')
    print('Please select or enter a department for the scan.')

    # Predefined list of departments (can be expanded as needed)
    departments = ['Agriculture and Agri-Food Canada', 'Environment and Climate Change Canada', 
                   'Health Canada', 'Transport Canada', 'Custom Department']

    print(Fore.CYAN + "Available departments:" + Fore.RESET)
    for i, dept in enumerate(departments, 1):
        print(f"{i}. {dept}")

    print("Enter the number corresponding to the department, or type a custom department name:")
    department_choice = input()

    if department_choice.isdigit() and 1 <= int(department_choice) <= len(departments):
        department = departments[int(department_choice) - 1]
    else:
        department = department_choice  # Allow custom department name input

    print(f"Scanning datasets for department: {department}")

    # PHASE 1: Inventorying the Open Data Portal (Registry)

    registry = RequestsDataCatalogue(REGISTRY_BASE_URL)
    registry_datasets: List[str] = registry.search_datasets(owner_org=department)
    print(Fore.GREEN)
    print(f'{len(registry_datasets)} datasets were found for the department {department} on the registry.' + Fore.RESET)

    # Create and update inventory
    inventory = Inventory()
    inventory.inventory(registry, registry_datasets)

    # FINISHING

    # Announcing total number of datasets and resources
    print()
    print(Fore.YELLOW + f'{len(inventory.datasets)}' + Fore.RESET,
            'datasets and',
            Fore.YELLOW + f'{len(inventory.resources)}' + Fore.RESET,
            'resources were found.')

    # Adding modified dates and compliances checks
    inventory.complete_missing_fields()
    # Completing empty fields
    inventory.datasets = inventory.datasets.fillna({
        'on_registry': False,
        'org': department,
        'org_title': department})

    # Exporting inventories
    print()
    inventory.export_datasets(path='./inventories/')
    inventory.export_resources(path='./inventories/')
    inventory.export_datasets(path='./inventories/',
                              filename='_latest_datasets_inventory.csv')
    inventory.export_resources(path='./inventories/',
                               filename='_latest_resources_inventory.csv')


if __name__ == '__main__':
    main()
