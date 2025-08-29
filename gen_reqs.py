import os
import re
import sys
import sysconfig
import importlib.metadata as metadata

def find_imports_in_file(filepath):
    """Extract top-level imports from a Python file."""
    imports = set()
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                parts = re.split(r'\s+', line)
                if parts[0] == "import":
                    modules = parts[1].split(",")
                    for mod in modules:
                        imports.add(mod.split(".")[0])
                elif parts[0] == "from":
                    imports.add(parts[1].split(".")[0])
    return imports

def find_imports_in_repo(root_dir="."):
    """Walk the repo and collect imports from all .py files."""
    all_imports = set()
    for subdir, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(subdir, fname)
                all_imports |= find_imports_in_file(fpath)
    return all_imports

def filter_stdlib(modules):
    """Filter out Python standard library modules."""
    stdlib_path = sysconfig.get_paths()["stdlib"]
    std_modules = set()
    for _, _, files in os.walk(stdlib_path):
        for fname in files:
            if fname.endswith(".py") and fname != "__init__.py":
                std_modules.add(fname[:-3])
    return {m for m in modules if m not in std_modules}

def map_to_installed_packages(modules):
    """
    Try to map module names to installed distributions using importlib.metadata.
    Not perfect, but works for most common packages.
    """
    results = []
    for dist in metadata.distributions():
        try:
            top_level = dist.read_text("top_level.txt")
            if not top_level:
                continue
            tops = top_level.splitlines()
            for mod in modules:
                if mod in tops:
                    results.append(f"{dist.metadata['Name']}=={dist.version}")
        except Exception:
            continue
    return sorted(set(results))

if __name__ == "__main__":
    modules = find_imports_in_repo(".")
    modules = filter_stdlib(modules)

    print("Found third-party imports:", modules)

    reqs = map_to_installed_packages(modules)

    print("\n--- requirements.txt ---")
    for r in reqs:
        print(r)
