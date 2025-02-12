# Deep Research Arxiv

![Logo](logo_a.png)

Deep Research Arxiv is a Streamlit-powered application designed to assist researchers in conducting comprehensive literature reviews using the Arxiv repository. This tool searches, analyzes, and synthesizes relevant papers into a cohesive literature review formatted in the Nature journal style.

## Features
- **Literature Search**: Query the Arxiv API to retrieve relevant research papers.
- **Paper Analysis**: Analyze selected papers and extract key information.
- **Automated Review Generation**: Leverage OpenRouter to generate detailed literature reviews.
- **Citation Formatting**: Provides formatted references and BibTeX entries for seamless citation integration.
- **Customizable API Configuration**: Easily configure your OpenRouter API key directly within the app.

## Installation

1. **Clone the Repository**
    ```
    git clone https://github.com/your-repo/deep-research-arxiv.git
    cd deep-research-arxiv
    ```

2. **Set Up a Virtual Environment (Optional but Recommended)**
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**
    ```
    pip install -r requirements.txt
    ```

4. **Place the Logo and Banner Images**
    - Ensure `logo_a.png` and `banner.png` are located in the root directory.

## Usage

1. **Configure API Key**
    - Launch the application with:
      ```
      streamlit run app.py
      ```
    - Use the sidebar in the app to enter and save your OpenRouter API key.

2. **Start Your Research**
    - Enter your research query and choose the number of papers to analyze.
    - Click the "🚀 Start Research" button to generate a comprehensive literature review.
    - Download the generated review along with well-formatted citations.

## File Structure
```
├── app.py                  # Main Streamlit application
├── research
│   └── arxiv_research.py   # Module handling Arxiv API and review generation
├── logo_a.png              # Repository logo
├── banner.png              # Banner image for the app
└── README.md               # This file
```


## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
