from app import app  # Expose the Flask app for Vercel serverless deployment 
import os
import requests
from flask import Response

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
            with open(svg_url, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            return Response(svg_content, mimetype='image/svg+xml')
    except Exception as e:
        return Response(f"Error generating SVG: {e}", mimetype='text/plain', status=500) 