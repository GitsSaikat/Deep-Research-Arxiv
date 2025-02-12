# app.py
import streamlit as st
from research import arxiv_research  # Import the corrected research module
import asyncio
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Deep Research Arxiv",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load images (Make sure you have these image files in your directory)
logo = Image.open('logo_a.png')  #  replace with your logo
banner = Image.open('banner.png') # replace with your banner


# Custom CSS (Optional - for styling)
st.markdown("""
    <style>
    .stImage > img {
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .api-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    .api-header {
        color: #1E88E5;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for API key configuration
if 'api_keys_configured' not in st.session_state:
    st.session_state.api_keys_configured = False

# Sidebar configuration for OpenRouter API key
with st.sidebar:
    st.image(logo, width=200, use_container_width=True)
    st.markdown("### ⚙️ API Configuration")

    with st.expander("Configure OpenRouter API Key", expanded=not st.session_state.api_keys_configured):
        api_form = st.form("api_keys_form")
        with api_form:
            openrouter_key = api_form.text_input(
                "OpenRouter API Key",
                type="password",
                value=st.session_state.get('openrouter_key', ''),
                help="Required for language model access (literature review generation)."
            )

            if api_form.form_submit_button("Save API Key"):
                if not openrouter_key:
                    st.error("❌ OpenRouter API key is required!")
                else:
                    st.session_state.openrouter_key = openrouter_key
                    st.session_state.api_keys_configured = True
                    st.success("✅ OpenRouter API key saved successfully!")
                    st.rerun()  # Re-run the app to update the state

    if st.session_state.api_keys_configured:
        st.success("✅ OpenRouter API Key configured")

    st.markdown("### 🔑 Get API Key")
    st.markdown("""
        - [OpenRouter API Key](https://openrouter.ai/keys)
    """)

# Main content area of the app
st.title("🔍 Deep Research Arxiv")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div style='background-color: #5dade2; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h4 style='color: #1565C0; margin-bottom: 0.5rem;'>Welcome to Deep Research Arxiv!</h4>
        <p style='color: #424242;'>
            This application helps you conduct literature reviews on Arxiv by:
            <br>
            • Searching Arxiv for relevant papers<br>
            • Analyzing upto 100 papers based on query<br>
            • Synthesizing a literature review with citations
        </p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("### Tips for Better Results")
    st.info("""
    
        • Be specific in your query with clear and focused questions.

        • Consider including relevant keywords.

        • Don't choose too many papers; it might prompt the model to include irrelevant information if not enough relevant papers exist.
    """)

with st.container():
    with st.form("research_form", clear_on_submit=False):
        st.markdown("### Research Parameters")

        user_query = st.text_area(
            "Research Query",
            placeholder="Enter your research topic or question here...",
            help="Be as specific as possible for better results (e.g., 'Quantum Machine Learning for Drug Discovery').",
            height=100,
            disabled=not st.session_state.api_keys_configured
        )
        
        paper_count = st.number_input(
            "Number of papers to analyze",
            min_value=10,
            max_value=100,
            value=20,
            step=5,
            help="Select number of papers to include (10-100)"
        )
        
        submitted = st.form_submit_button(
            "🚀 Start Research",
            disabled=not st.session_state.api_keys_configured
        )

        if not st.session_state.api_keys_configured:
            st.warning("⚠️ Please configure your OpenRouter API key in the sidebar to enable research.")
    
    


# Function to run the research (using asyncio.run)
def run_research(user_query, paper_count):
    """Execute research with specified paper count."""
    arxiv_research.OPENROUTER_API_KEY = st.session_state.openrouter_key
    return asyncio.run(arxiv_research.research_flow(user_query, paper_count))


# Handling form submission and displaying results
if submitted and st.session_state.api_keys_configured:
    if not user_query.strip():
        st.error("⚠️ Please enter a research query.")
    else:
        with st.spinner(f"🔄 Analyzing {paper_count} papers from Arxiv..."):
            try:
                literature_review = run_research(user_query, paper_count)
                
                # Display results
                st.markdown("""
                    <div class='report-container'>
                        <h3 style='color: #1E88E5; margin-bottom: 1rem;'>📊 Literature Review</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(literature_review, unsafe_allow_html=False)
                
                # Extract citation statistics
                if "Citation Statistics:" in literature_review:
                    stats_section = literature_review.split("Citation Statistics:")[-1]
                    st.info(f"📈 Citation Statistics:{stats_section}")
                
                st.download_button(
                    label="📥 Download Literature Review",
                    data=literature_review,
                    file_name="nature_style_review.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Built by GItsSaikat ❤️</p>
    </div>
""", unsafe_allow_html=True)