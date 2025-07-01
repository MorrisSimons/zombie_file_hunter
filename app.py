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
        return f'<html><body><h2>SVG Import Graph</h2><a href="{svg_url}">View SVG (new tab)</a><br><img src="{svg_url}" style="max-width:100%; border:1px solid #ccc; margin-top:10px;"></body></html>'
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