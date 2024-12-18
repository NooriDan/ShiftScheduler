from ortools_scheduler import domain, solver, utils
import ortools_scheduler

from pprint import pprint
import os

def clear():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux/macOS
        os.system('clear')

clear()


module = ortools_scheduler
print(f"=== {module.__name__} ===")
pprint(dir(module))
print(f"__all__: {module.__all__}\n")
# pprint(f"__builtins__: {module.__builtins__}\n")
print(f"__doc__: {module.__doc__}\n")
print(f"__file__: {module.__file__}\n")
print(f"__package__: {module.__package__}\n")
print(f"__spec__: {module.__spec__}\n")
print(f"__path__: {module.__path__}\n")


module = domain
print(f"=== {module.__name__} ===")
pprint(dir(module))
# pprint(f"__builtins__: {module.__builtins__}\n")
print(f"__doc__: {module.__doc__}\n")
print(f"__file__: {module.__file__}\n")
print(f"__package__: {module.__package__}\n")
print(f"__spec__: {module.__spec__}\n")
