# Zombie File Hunter - GitHub Repository Analyzer for Lovable Projects
![top language](https://img.shields.io/github/languages/top/gpt-null/template)
![code size](https://img.shields.io/github/languages/code-size/gpt-null/template)
![last commit](https://img.shields.io/github/last-commit/gpt-null/template)
![issues](https://img.shields.io/github/issues/gpt-null/template)
![contributors](https://img.shields.io/github/contributors/gpt-null/template)
![License](https://img.shields.io/github/license/gpt-null/template)

### TL;DR
- this project finds unsued files in a lovable repository
- Purpose; keep the codebase clean and minimalistic

## Story

When I used Loveable, I found it generated code and functions that I sometimes didn't want. When I deleted larger components or pages that had multiple subcomponents, I discovered that some of the related files remained in the repository was unused. I wanted to clean up the codebase and remove these unused files.

#### This is the page we will use for our sample:

![Sample page interface](assets/image-2.png)

**Link to code:** [https://github.com/MorrisSimons/sample\_test\_page](https://github.com/MorrisSimons/sample_test_page)

#### The first image below doesn't say much; except that many files are not used in the project. It also demonstrates what the output looks like:

![Console output showing analysis results](assets/image.png)

#### We only want to look at a small portion of the image; that covers four points to help understand different parts of the project:

![Dependency graph visualization showing used and unused files](assets/image-3.png)

* An unused externally added file (marked red). The file `testapge.tsx` is not used (left of `main.tsx`).
* Unused files located in `components/ui/...` (marked red), for example, the file to the right of `main.tsx`.
* Unused UI components (marked red) connected to `components/ui/button.tsx`. The button itself is used, so it's marked blue.
* Used files like `pages/NotFound.tsx`, also marked blue.

**Important notes about the code:**
* All the redfiles are unsued and all the blue ones are used in the main.tsx file.
* Files in the UI folder are typically generated uniformly for all projects but aren't always utilized. This explains why the sample repository has many unused files.
* Some files might be connected indirectly (e.g., to `button.tsx`) but remain unused by the main project. All `.js`, `.jsx`, `.ts`, `.tsx`, and `.css` files not directly connected to the main project are marked red.

The primary purpose of this project is not just cleaning up the UI folder but identifying unused or forgotten files, such as leftover subcomponents like `testapge.tsx`. If you're interested, you can explore a larger example project in the `assets` folder of this repository.

## Example Outputs

This repository includes several example outputs in the `assets/` folder and here in the main project folder:
- **Real Estate Mapstore**: [`assets/import_graph_realestate-mapstore.svg`](assets/import_graph_realestate-mapstore.svg) - Analysis of a larger, more complex project
- **Sample Test Page Analysis**: [`import_graph_sample_test_page.svg`](import_graph_sample_test_page.svg) - Analysis of the sample repository mentioned above
Each analysis generates both `.dot` (source) and `.svg` (visual) files that show the dependency relationships between files in your project.

### Aim of this Project:

I want to identify and suggest removal of unused files to maintain clean, minimalistic, and readable codebase for lovable projects.

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Public Repositories

```bash
python main.py "https://github.com/MorrisSimons/sample_test_page"
```

**Or just run the program and provide the URL when prompted:**

```
'https://github.com/MorrisSimons/sample_test_page'
```

### Private Repositories

For private repositories, set your GitHub token:

```bash
export GITHUB_TOKEN=your_github_token_here
python main.py owner/private-repo
```

### Complete Example

Here's a full example, including activating a virtual environment, setting the GitHub token, and analyzing a repository with target file highlighting:

```bash
export GITHUB_TOKEN=GH_token && python main.py "https://github.com/MorrisSimons/realestate-mapstore" myCompanies.tsx
```

This command will:
- Download and analyze the repository
- Highlight all files connected to `myCompanies.tsx` in green
- Mark non-code files (images, PDFs, CSS) in yellow
- Show unused files in red
- Generate both `.dot` and `.svg` visualization files

**Sample Output:**
```
Found 102 code files and 8 other files (110 total)
Graph: 110 nodes, 160 edges
Connected components: 73
Unused components: 37
```

## How It Works

1. **Repository Download:** Clones the repository (preferred) or downloads a ZIP as fallback.
2. **Source Discovery:** Identifies the main source directory (`src/` or root).
3. **File Scanning:** Searches for all relevant files including:
   - Code files: JavaScript/TypeScript files (`.js`, `.jsx`, `.ts`, `.tsx`)
   - Asset files: Images, documents, and other resources (`.png`, `.jpg`, `.pdf`, `.webp`, `.css`, `.md`, etc.)
4. **Import Analysis:** Extracts import statements and resolves file paths for code files.
5. **Graph Building:** Builds a directed graph representing file dependencies.
6. **Unused Detection:** Finds files not reachable from the main entry points.
7. **Target Analysis:** Optionally highlights files connected to a specific target file.
8. **Visualization:** Produces visual graphs in DOT and SVG formats.

## Output

The tool provides:

* **Console Output:** Summary report, including count of unused files and file type breakdown.
* **DOT File:** Dependency graph in DOT format (`import_graph_<repo>.dot`).
* **SVG File:** Visual graph with color-coded nodes (requires Graphviz):

### Color Coding System

* 🟢 **Light Green:** Files connected to the target file (when specified, e.g., `myCompanies.tsx`)
* 🟡 **Yellow:** Non-code files (assets, documents, CSS, etc.)
* 🟠 **Orange:** UI component files (`components/ui/`)
* 🔵 **Light Blue:** Used/connected code files
* 🔴 **Red:** Unused or "zombie" files

### Usage with Target File

To highlight files connected to a specific component:

```bash
python main.py "https://github.com/owner/repo" myCompanies.tsx
```

This will mark all files that are dependencies of `myCompanies.tsx` in light green, making it easy to see which files are specifically related to that component.

## TODO:
- [x] ~~Fix the README to explain the new updates~~ - **COMPLETED**
- [x] ~~Add yellow color for non-code files (assets, PDFs, etc.)~~ - **COMPLETED** 
- [x] ~~Add target file highlighting with green color~~ - **COMPLETED**
- [ ] Fix arguments input repo error handling
- [ ] Add automated testing for different scenarios where unused files are created
- [ ] Improve detection of files imported in headers but not used in the project
- [ ] Add delete function for unused files
- [ ] Build it as an API
- [ ] Build it in Go
- [ ] Build it as a Docker container 
