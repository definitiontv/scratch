import os
import subprocess
from pathlib import Path
import markdown
from weasyprint import HTML
import shutil

REPO_URL = "https://github.com/open-webui/docs.git"
TEMP_DIR = Path("/tmp/openwebui_docs")
OUTPUT_PDF = Path("/tmp/openwebui_documentation.pdf")

def install_dependencies():
    """Install required Python packages"""
    subprocess.run(["pip", "install", "markdown", "weasyprint"], check=True)

def clone_docs():
    """Clone the documentation repository"""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    subprocess.run(["git", "clone", "--depth=1", REPO_URL, TEMP_DIR], check=True)

def process_markdown():
    """Convert all markdown files to a single HTML string with styling"""
    css = """
    body { font-family: sans-serif; line-height: 1.6; margin: 2em; }
    h1 { border-bottom: 2px solid #ddd; }
    code { background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
    pre { background: #f8f8f8; padding: 1em; overflow: auto; }
    """
    
    html_content = f"<html><head><style>{css}</style></head><body>"
    
    for root, _, files in os.walk(TEMP_DIR):
        for file in sorted(files):
            if file.endswith(".md"):
                path = Path(root) / file
                with open(path, "r") as f:
                    md_content = f.read()
                    html_content += markdown.markdown(md_content)
                    html_content += "<hr/>"
    
    html_content += "</body></html>"
    return html_content

def generate_pdf(html_content):
    """Generate PDF from HTML content"""
    HTML(string=html_content).write_pdf(OUTPUT_PDF)

if __name__ == "__main__":
    #install_dependencies()
    clone_docs()
    html_content = process_markdown()
    generate_pdf(html_content)
    print(f"PDF generated at: {OUTPUT_PDF}")

