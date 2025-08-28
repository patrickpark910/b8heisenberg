import os
import re
import pkg_resources

def find_imports_in_file(filepath):
    """Extract import statements from a file."""
    imports = set()
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            # Match "import x" or "from x import ..."
            if line.startswith("import ") or line.startswith("from "):
                parts = re.split(r'\s+', line)
                if parts[0] == "import":
                    # import foo, bar
                    modules = parts[1].split(",")
                    for mod in modules:
                        imports.add(mod.split(".")[0])
                elif parts[0] == "from":
                    imports.add(parts[1].split(".")[0])
    return imports

def find_imports_in_repo(root_dir="."):
    """Walk repo and collect imports from all .py files."""
    all_imports = set()
    for subdir, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(subdir, fname)
                all_imports |= find_imports_in_file(fpath)
    return all_imports

def map_to_installed_packages(modules):
    """Map module names to actual installed package names."""
    installed = {pkg.key: pkg for pkg in pkg_resources.working_set}
    results = []
    for mod in sorted(modules):
        for pkg_name, pkg in installed.items():
            try:
                if mod == pkg.key or mod == pkg.project_name.lower():
                    results.append(f"{pkg.project_name}=={pkg.version}")
                    break
            except Exception:
                pass
    return sorted(set(results))

if __name__ == "__main__":
    modules = find_imports_in_repo(".")
    print("Found modules:", modules)

    # Map to installed packages with version pins
    reqs = map_to_installed_packages(modules)

    print("\n--- requirements.txt ---")
    for r in reqs:
        print(r)
