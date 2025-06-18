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

When I used Loveable, I found it generated code and functions that I sometimes didn't want. When I deleted larger components or pages that had multiple subcomponents, I discovered that the related files remained in the repository creating a mess with alot of unused files. I wanted to clean up the codebase and remove these unused files.

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

Here's a full example, including activating a virtual environment, setting the GitHub token, and analyzing a repository:

```bash
export GITHUB_TOKEN=GH_token && python main.py "https://github.com/MorrisSimons/sample_test_page"
```

## How It Works

1. **Repository Download:** Clones the repository (preferred) or downloads a ZIP as fallback.
2. **Source Discovery:** Identifies the main source directory (`src/` or root).
3. **File Scanning:** Searches for JavaScript/TypeScript files (`.js`, `.jsx`, `.ts`, `.tsx`).
4. **Import Analysis:** Extracts import statements and resolves file paths.
5. **Graph Building:** Builds a directed graph representing file dependencies.
6. **Unused Detection:** Finds files not reachable from the main entry points.
7. **Visualization:** Produces visual graphs in DOT and SVG formats.

## Output

The tool provides:

* **Console Output:** Summary report, including count of unused files.
* **DOT File:** Dependency graph in DOT format (`import_graph_<repo>.dot`).
* **SVG File:** Visual graph with color-coded nodes (requires Graphviz):

  * 🔵 **Blue:** Used or connected files
  * 🔴 **Red:** Unused or "zombie" files


## TODO:
- Fix the read me to exaplain the new updates.
- Do some fixes for yellow unwanted files.
- Do some test to replicate diffrent scenarios where not used files are created.
- Some files are imported in the header but not used in the project.
- No delete function yet.
- Build it as a API
- Build it in Go
- Build it as a docker 
