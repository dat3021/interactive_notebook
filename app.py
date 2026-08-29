import os
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="HTML Notebook Viewer",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Sleek Dark Glassmorphism Theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* ── Global Styles ── */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
        min-height: 100vh;
        color: #f3f4f6;
    }

    /* ── Sidebar Styling ── */
    [data-testid="stSidebar"] {
        background: rgba(17, 24, 39, 0.7);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #f3f4f6;
        font-weight: 700;
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Make buttons in sidebar look like clean menu list items */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: rgba(255, 255, 255, 0.02) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 8px;
        text-align: left;
        display: flex;
        justify-content: flex-start;
        padding: 8px 12px;
        transition: all 0.2s ease-in-out;
        font-size: 0.9rem;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(99, 102, 241, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #e0e7ff !important;
        transform: translateX(2px);
    }

    /* ── Main View Glassmorphism Card ── */
    .viewer-header {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(12px);
    }
    
    .viewer-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .viewer-header p {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* File Tree Expander Tweaks */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        color: #e2e8f0;
        font-size: 0.9rem;
        font-weight: 600;
    }

    /* Maximize main content space to fill page */
    .main .block-container,
    [data-testid="stAppViewBlockContainer"] {
        max-width: 100% !important;
        width: 100% !important;
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        margin: 0px !important;
    }

    /* Make vertical layout container fill full width */
    [data-testid="stVerticalBlock"] {
        padding: 0rem !important;
        gap: 0rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Make each element container fill full width */
    div.element-container,
    div[data-testid="element-container"] {
        padding: 0rem !important;
        margin: 0rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Target all iframes and force them to stretch full width */
    iframe[title="streamlit_components.v1.html"],
    [data-testid="stHtml"] iframe,
    iframe {
        width: 100% !important;
        max-width: 100% !important;
        border: none !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* Transparent header to keep sidebar toggle button visible */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        border-bottom: none !important;
        color: #f3f4f6 !important;
    }

    /* ── Iframe container border ── */
    .iframe-wrapper {
        border: none !important;
        border-radius: 0px !important;
        overflow: hidden;
        background: #ffffff; /* Fallback white background for web content */
        width: 100% !important;
        max-width: 100% !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Path Sandboxing & Security Check
# ---------------------------------------------------------------------------
# Define current file directory as the base/sandbox folder
# Enforce a trailing slash/separator to prevent partial matching bypasses
SANDBOX_DIR = os.path.abspath(os.path.dirname(__file__)) + os.sep

def secure_read_html(file_path):
    """
    Validates that file_path resides strictly within SANDBOX_DIR
    and is of type '.html' to prevent directory traversal.
    """
    abs_path = os.path.abspath(file_path)
    
    # Verify sandbox boundary check
    if not abs_path.startswith(SANDBOX_DIR):
        st.error("🔒 Security Exception: Path traversal attempt blocked.")
        # Fail close
        raise PermissionError(f"Access denied: {file_path} is outside the allowed directory.")
        
    # Verify extension
    if not abs_path.endswith(".html"):
        st.error("🔒 Security Exception: Invalid file format.")
        raise ValueError("Only HTML files are allowed to be loaded.")
        
    with open(abs_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # JS helper to prevent hash clicks from navigating the iframe URL (which breaks inside srcdoc/sandboxed frames)
    # and to force external links to open in a new tab.
    injection_script = """
    <script>
    (function() {
        function setupIframeLinks() {
            // 1. Handle hash links (smooth scroll within iframe, bypass about:srcdoc navigation bugs)
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.removeEventListener('click', handleHashClick);
                anchor.addEventListener('click', handleHashClick);
            });

            // 2. Force external links to open in a new tab (prevent CORS/sandbox frame load block)
            document.querySelectorAll('a').forEach(link => {
                const href = link.getAttribute('href');
                if (href && (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('//'))) {
                    link.setAttribute('target', '_blank');
                    link.setAttribute('rel', 'noopener noreferrer');
                }
            });
        }

        function handleHashClick(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            const targetId = href ? href.substring(1) : null;
            if (targetId) {
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    // Update URL hash without reloading the iframe
                    history.pushState(null, null, '#' + targetId);
                }
            }
        }

        // Run immediately and on page load events
        setupIframeLinks();
        window.addEventListener('load', setupIframeLinks);
        document.addEventListener('DOMContentLoaded', setupIframeLinks);
    })();
    </script>
    """

    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{injection_script}</body>")
    else:
        html_content = html_content + injection_script

    return html_content

# ---------------------------------------------------------------------------
# Directory Scanning & Tree Builder
# ---------------------------------------------------------------------------
def scan_html_files(base_dir):
    """
    Recursively scan the base directory for HTML files,
    ignoring hidden folders (like .git).
    """
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        # Filter out hidden folders in-place to prevent traversing them
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.html'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                html_files.append((rel_path, full_path))
    return sorted(html_files, key=lambda x: x[0].lower())

def build_tree(files_list):
    """
    Build a nested dictionary tree from flat relative paths.
    """
    tree = {}
    for rel_path, full_path in files_list:
        parts = rel_path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = full_path
    return tree

# Initialize folder scan cache in session state
if "html_files_tree" not in st.session_state or "html_files_list" not in st.session_state:
    html_files = scan_html_files(SANDBOX_DIR)
    st.session_state.html_files_list = html_files
    st.session_state.html_files_tree = build_tree(html_files)

# ---------------------------------------------------------------------------
# Sidebar Layout
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("📂 Notebook Viewer")
    st.write("Dynamic file browser for HTML pages")

    # Refresh Button
    if st.button("🔄 Refresh Files", use_container_width=True):
        html_files = scan_html_files(SANDBOX_DIR)
        st.session_state.html_files_list = html_files
        st.session_state.html_files_tree = build_tree(html_files)
        st.success("File index updated!")
        st.rerun()

    st.markdown("---")

    # Search / Filter Box
    search_query = st.text_input("🔍 Search files...", "").strip().lower()

    # Viewer Height Controller
    view_height = st.slider("📏 Adjust View Height (px)", min_value=400, max_value=3000, value=1000, step=100)
    
    st.markdown("---")
    st.write("📁 **File Structure**")

    # Process search query filtering if active
    if search_query:
        filtered_files = [
            (rel, full) for rel, full in st.session_state.html_files_list
            if search_query in rel.lower() or search_query in os.path.basename(full).lower()
        ]
        display_tree = build_tree(filtered_files)
    else:
        display_tree = st.session_state.html_files_tree

    # Recursive Tree Renderer
    def render_tree(node, current_path=""):
        # Sort node keys: directories (dict) first, then files (str)
        sorted_keys = sorted(
            node.keys(),
            key=lambda k: (0 if isinstance(node[k], dict) else 1, k.lower())
        )
        for name in sorted_keys:
            content = node[name]
            if isinstance(content, dict):
                # Directory
                with st.expander(f"📁 {name}", expanded=True):
                    render_tree(content, os.path.join(current_path, name))
            else:
                # File
                is_selected = st.session_state.get("selected_file") == content
                label = f"👉 {name}" if is_selected else f"📄 {name}"
                if st.button(label, key=content, use_container_width=True):
                    st.session_state.selected_file = content
                    st.rerun()

    if not display_tree:
        st.info("No HTML files found.")
    else:
        render_tree(display_tree)

# ---------------------------------------------------------------------------
# Main Panel View
# ---------------------------------------------------------------------------
selected_file = st.session_state.get("selected_file")

if selected_file and os.path.exists(selected_file):
    try:
        # Load file content securely
        html_content = secure_read_html(selected_file)
        
        # Render HTML page using iframe components
        st.markdown('<div class="iframe-wrapper">', unsafe_allow_html=True)
        components.html(html_content, height=view_height, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")

else:
    # Beautiful welcome/empty state
    st.markdown(
        """
        <div style="text-align: center; padding: 5rem 2rem; background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 20px; backdrop-filter: blur(10px);">
            <h1 style="background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">
                Welcome to Notebook Explorer 📁
            </h1>
            <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 0 auto 2rem;">
                Select a file from the sidebar directory structure to view its contents. You can search files, adjust the viewer height, and refresh directory listing dynamically.
            </p>
            <div style="display: inline-flex; gap: 10px; color: #a78bfa; font-size: 0.95rem; font-weight: 500;">
                <span>🔍 Search Support</span> • 
                <span>🔒 Security Sandboxed</span> • 
                <span>⚡ Real-time Rerendering</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
