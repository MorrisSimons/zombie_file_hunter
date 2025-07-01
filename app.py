from flask import Flask, Response, send_file
import os
from main import generate_svg_for_github_repo
import requests

app = Flask(__name__)

@app.route('/')
def landing_page():
    return '''
    <html>
    <head><title>Zombie File Hunter</title></head>
    <body>
        <h1>Welcome to Zombie File Hunter!</h1>
        <p>To view a GitHub repo's import graph, use a URL like:</p>
        <code>https://g.morrissimons.com/&lt;username&gt;/&lt;repo&gt;</code>
        <p>Example: <a href="/MorrisSimons/sample_test_page">/MorrisSimons/sample_test_page</a></p>
    </body>
    </html>
    '''

@app.route('/<username>/<repo>')
def repo_svg(username, repo):
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        svg_url = generate_svg_for_github_repo(username, repo, github_token=github_token)
        if svg_url.startswith('http://') or svg_url.startswith('https://'):
            # Fetch the SVG content from the URL
            svg_response = requests.get(svg_url)
            svg_response.raise_for_status()
            return Response(svg_response.content, mimetype='image/svg+xml')
        else:
            # Local file path
            if os.path.exists(svg_url):
                with open(svg_url, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                return Response(svg_content, mimetype='image/svg+xml')
            else:
                # Try remote cache as fallback
                username_repo = os.path.basename(svg_url).replace('svg_', '').replace('.svg', '')
                blob_filename = f"svg/{username_repo}.svg"
                blob_url = f"https://blob.vercel-storage.com/api/blob/{blob_filename}"
                try:
                    svg_response = requests.get(blob_url)
                    if svg_response.status_code == 200:
                        return Response(svg_response.content, mimetype='image/svg+xml')
                except Exception:
                    pass
                return Response("SVG not found in local or remote cache.", mimetype='text/plain', status=404)
    except Exception as e:
        return Response(f"Error generating SVG: {e}", mimetype='text/plain', status=500)

# Note: SVG caching is handled in main.py (generate_svg_for_github_repo). This route always serves the cached SVG if available.

def dot_to_svg(dot_code):
    url = 'https://kroki.io/graphviz/svg'
    headers = {'Content-Type': 'text/plain'}
    response = requests.post(url, headers=headers, data=dot_code.encode('utf-8'))
    response.raise_for_status()
    return response.text  # This is the SVG as a string

if __name__ == '__main__':
    app.run(debug=True) 