import os
import re
import sys
import tempfile
import pathlib
import subprocess
import json
from urllib.parse import urlparse

import networkx as nx
import requests
from zip_file_helper_function import _download_zip_repo

# Configuration
ALIASES = {"@/": "src/"}
SKIP_FILES = [
    "lib/utils.ts", "lib/utils.tsx", 
    "hooks/use-toast.ts", "components/ui/use-toast.ts",
    "components/ui/toast.tsx", "components/ui/toaster.tsx"
]
SKIP_PATTERNS = ["node_modules", ".git", "dist", "build", ".next", "__pycache__", ".vscode", ".idea"]
EXTERNAL_PACKAGES = ['react', 'typescript', 'next', 'axios', 'lodash', '@radix-ui']


def download_repo(repo_url, temp_dir, github_token=None):
    """Download GitHub repo using git clone or ZIP fallback"""
    # Parse URL to get owner/repo
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip('/').split('/')
    owner, repo = path_parts[0], path_parts[1]
    
    clone_dir = temp_dir / repo
    
    # Try git clone first
    try:
        clone_url = repo_url
        if github_token:
            clone_url = repo_url.replace("https://github.com/", f"https://{github_token}@github.com/")
        
        cmd = ["git", "clone", "--depth", "1", clone_url, str(clone_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and clone_dir.exists():
            return clone_dir
    except:
        pass
    
    # Fallback to ZIP download
    session = requests.Session()
    if github_token:
        session.headers.update({"Authorization": f"token {github_token}"})
    
    return _download_zip_repo(repo_url, temp_dir, owner, repo, session, github_token)


def find_src_directory(repo_dir):
    """Find the main source directory (src/ or project root with package.json)"""
    # Look for package.json files
    package_files = [f for f in repo_dir.rglob("package.json") if "node_modules" not in str(f)]
    
    if package_files:
        # Use the one closest to root
        package_json = min(package_files, key=lambda x: len(x.parts))
        
        try:
            with open(package_json) as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                # Check if it's a React/TypeScript project
                if any(dep in deps for dep in ["react", "typescript", "@types/react", "next", "vite"]):
                    project_root = package_json.parent
                    src_dir = project_root / "src"
                    return src_dir if src_dir.exists() else project_root
        except:
            pass
    
    # Fallback: find src directory
    src_dirs = [d for d in repo_dir.rglob("src") if d.is_dir() and "node_modules" not in str(d)]
    return src_dirs[0] if src_dirs else repo_dir


def should_skip_file(file_path):
    """Check if file should be skipped"""
    file_str = str(file_path)
    
    # Skip exact matches
    for skip_file in SKIP_FILES:
        if file_str.endswith(skip_file):
            return True
    
    # Skip pattern matches
    for pattern in SKIP_PATTERNS:
        if pattern in file_str:
            return True
    
    return False


def should_include_non_code_file(file_path):
    """Check if non-code file should be included in the graph"""
    # Include common asset and document types
    included_extensions = {
        '.pdf', '.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg',
        '.md', '.txt', '.json', '.xml', '.yaml', '.yml',
        '.css', '.scss', '.sass', '.less',
        '.html', '.htm'
    }
    
    # Skip very large files or temporary files
    excluded_patterns = [
        '.log', '.tmp', '.cache', '.lock', 
        'package-lock.json', 'yarn.lock', '.env'
    ]
    
    file_str = str(file_path)
    extension = file_path.suffix.lower()
    
    # Skip excluded patterns
    for pattern in excluded_patterns:
        if pattern in file_str.lower():
            return False
    
    # Include if it has an included extension
    return extension in included_extensions


def get_imports(code):
    """Extract import paths from code"""
    patterns = [
        r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',  # import ... from "path"
        r'import\s+[\'"]([^\'"]+)[\'"]',                # import "path"
        r'export\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',  # export ... from "path"
    ]
    
    imports = []
    for pattern in patterns:
        imports.extend(re.findall(pattern, code, re.MULTILINE))
    
    return imports


def resolve_import(import_path, source_file, root_dir):
    """Convert import path to actual file path"""
    # Skip external packages
    for pkg in EXTERNAL_PACKAGES:
        if pkg in import_path:
            return None
    
    # Skip utility imports that create hub nodes
    utility_patterns = [
        'lib/utils', '@/lib/utils', './lib/utils', '../lib/utils',
        'use-toast', 'toast', 'toaster'
    ]
    for pattern in utility_patterns:
        if pattern in import_path:
            return None
    
    # Skip non-local imports
    if not import_path.startswith('.') and not import_path.startswith('@/') and not import_path.startswith('src/'):
        return None
    
    # Apply aliases
    for alias, replacement in ALIASES.items():
        if import_path.startswith(alias):
            import_path = import_path.replace(alias, replacement, 1)
            break
    
    # Resolve path
    if import_path.startswith('./') or import_path.startswith('../'):
        target = (source_file.parent / import_path).resolve()
    elif import_path.startswith('src/'):
        target = (root_dir / import_path[4:]).resolve()  # Remove 'src/'
    else:
        target = (root_dir / import_path).resolve()
    
    # Try different extensions
    for ext in ['', '.tsx', '.ts', '.jsx', '.js']:
        candidate = target.with_suffix(ext) if ext else target
        if candidate.exists() and candidate.is_file():
            return candidate
    
    # Try index files
    if target.is_dir():
        for index_file in ['index.tsx', 'index.ts', 'index.jsx', 'index.js']:
            candidate = target / index_file
            if candidate.exists():
                return candidate
    
    return None


def analyze_repository(root_dir, repo_name, my_companies_file=None):
    """Main analysis function"""
    print(f"Analyzing {repo_name} in {root_dir}")
    
    # Find all source files (code files)
    code_files = []
    for pattern in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
        code_files.extend(root_dir.rglob(pattern))
    
    # Filter code files
    code_files = [f for f in code_files 
                  if not f.name.endswith('.d.ts') and 
                  not should_skip_file(f.relative_to(root_dir))]
    
    # Find all other files (non-code files like PDFs, images, etc.)
    all_files = []
    for file in root_dir.rglob("*"):
        if file.is_file() and not should_skip_file(file.relative_to(root_dir)):
            all_files.append(file)
    
    # Separate code files from other files
    code_extensions = {'.ts', '.tsx', '.js', '.jsx', '.d.ts'}
    other_files = [f for f in all_files 
                   if f.suffix.lower() not in code_extensions and 
                   should_include_non_code_file(f)]
    
    # Combine all files
    files = code_files + other_files
    
    print(f"Found {len(code_files)} code files and {len(other_files)} other files ({len(files)} total)")
    
    # Build import graph
    graph = nx.DiGraph()
    
    for file in files:
        file_rel = str(file.relative_to(root_dir))
        graph.add_node(file_rel)
    
    # Add edges for imports (only for code files)
    for file in code_files:
        try:
            code = file.read_text(encoding='utf-8')
            imports = get_imports(code)
            file_rel = str(file.relative_to(root_dir))
            
            for import_path in imports:
                resolved = resolve_import(import_path, file, root_dir)
                if resolved and resolved != file:
                    try:
                        target_rel = str(resolved.relative_to(root_dir))
                        graph.add_edge(file_rel, target_rel, dir='back')
                    except ValueError:
                        continue  # Outside root directory
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Find entry points and unused components
    entry_points = [node for node in graph.nodes() if node in ["main.tsx", "index.tsx", "App.tsx"]]
    if not entry_points and graph.nodes():
        entry_points = [list(graph.nodes())[0]]  # Use first file as fallback
    
    # Find reachable nodes
    connected = set()
    if entry_points and graph.number_of_edges() > 0:
        for entry in entry_points:
            if entry in graph:
                connected.update(nx.descendants(graph, entry))
                connected.add(entry)
    
    unused = [node for node in graph.nodes() if node not in connected]
    
    # Find files connected to myCompanies.tsx if specified
    my_companies_connected = set()
    if my_companies_file and my_companies_file in graph:
        my_companies_connected.update(nx.descendants(graph, my_companies_file))
        my_companies_connected.add(my_companies_file)
    
    print(f"\nResults:")
    print(f"Entry points: {entry_points}")
    print(f"Connected components: {len(connected)}")
    print(f"Unused components: {len(unused)}")
    
    if unused:
        print("\nUnused files:")
        for file in unused:
            print(f"  - {file}")
    
    # Generate visualization
    output_file = f"import_graph_{repo_name.replace('/', '_')}"
    
    # Color nodes
    for node in graph.nodes():
        # Get file extension to determine if it's a code file
        node_path = root_dir / node
        is_code_file = node_path.suffix.lower() in {'.ts', '.tsx', '.js', '.jsx'}
        
        if not is_code_file:
            # Non-code files (PDFs, images, etc.) get yellow color
            graph.nodes[node]['color'] = 'yellow'
        elif my_companies_file and node in my_companies_connected:
            graph.nodes[node]['color'] = 'lightgreen'
        elif 'components/ui' in node.lower():
            graph.nodes[node]['color'] = 'orange'
        elif node in connected:
            graph.nodes[node]['color'] = 'lightblue'
        else:
            graph.nodes[node]['color'] = 'red'
        graph.nodes[node]['style'] = 'filled'
    
    # Write DOT file
    nx.drawing.nx_pydot.write_dot(graph, f"{output_file}.dot")
    
    # Generate SVG
    try:
        subprocess.run(["dot", "-Tsvg", f"{output_file}.dot", "-o", f"{output_file}.svg"], check=True)
        print(f"Generated {output_file}.svg")
    except:
        print("Install Graphviz to generate SVG files")


def main():
    """Main entry point"""
    print("GitHub Repository Analyzer")
    print("=" * 30)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if len(sys.argv) > 1:
        repo_input = sys.argv[1].strip()
        if repo_input.startswith('https://github.com/'):
            repo_url = repo_input
        elif '/' in repo_input:
            repo_url = f"https://github.com/{repo_input}"
        else:
            print("Use: python script.py owner/repo [myCompanies.tsx]")
            return
        
        # Check for target file argument
        if len(sys.argv) > 2:
            target_file = sys.argv[2].strip()
            
        repo_url = input("GitHub repo URL: ").strip()
    
    if not repo_url:
        return
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            
            # Download repo
            repo_dir = download_repo(repo_url, temp_path, github_token)
            
            # Find source directory
            src_dir = find_src_directory(repo_dir)
            
            # Analyze
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            analyze_repository(src_dir, repo_name, target_file)
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
