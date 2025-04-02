# research/arxiv_research.py
import asyncio
import aiohttp
import nest_asyncio
import xml.etree.ElementTree as ET  # For parsing Arxiv XML response
nest_asyncio.apply()

# API Endpoints
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# Global API Key (You'll set this in app.py)
OPENROUTER_API_KEY = ""
DEFAULT_MODEL = "google/gemini-2.5-pro-exp-03-25:free"

FIXED_PAPER_COUNT = 70  
async def call_openrouter_async(session, messages, model=DEFAULT_MODEL):
    """
    Make an asynchronous request to the OpenRouter chat completion API.
    Returns the assistant's reply text.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/Pygen",
        "X-Title": "Arxiv Literature Review Assistant",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096
    }

    try:
        async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result['choices'][0]['message']['content']
            else:
                text = await resp.text()
                print(f"OpenRouter API error: {resp.status} - {text}")
                return None
    except Exception as e:
        print("Error during OpenRouter call:", e)
        return None

async def search_arxiv_async(session, query, max_results=100):
    """
    Search Arxiv API (no API key needed) and return paper entries.
    """
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    paper_entries = []
    try:
        async with session.get(ARXIV_API_URL, params=params) as response:
            if response.status == 200:
                xml_content = await response.text()
                root = ET.fromstring(xml_content)
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}

                entries = root.findall('atom:entry', namespace)
                for entry in entries:
                    title_element = entry.find('atom:title', namespace)
                    abstract_element = entry.find('atom:summary', namespace)
                    url_element = entry.find('atom:id', namespace)
                    authors_elements = entry.findall('atom:author/atom:name', namespace)
                    published_element = entry.find('atom:published', namespace)  # Get publication date

                    authors = [author.text for author in authors_elements] if authors_elements else ["N/A"]
                    title = title_element.text.strip() if title_element is not None else "N/A"
                    abstract = abstract_element.text.strip().replace('\n', ' ') if abstract_element is not None else "N/A"
                    url = url_element.text.strip() if url_element is not None else "N/A"
                    published = published_element.text.strip() if published_element is not None else "N/A"
                    year = published[:4] if published else "N/A" #Extract the year.

                    paper_entries.append({
                        'title': title,
                        'abstract': abstract,
                        'url': url,
                        'authors': ', '.join(authors),
                        'year': year
                    })
            else:
                print(f"Arxiv API error: {response.status}")
                return []
    except Exception as e:
        print(f"Error during Arxiv API call: {e}")
        return []
    return paper_entries

async def prepare_references(paper_entries):
    """Prepare reference list from paper entries"""
    references = []
    for idx, paper in enumerate(paper_entries, 1):
        references.append({
            'citation_number': idx,
            'authors': paper['authors'],
            'title': paper['title'],
            'year': paper['year'],
            'url': paper['url'],
            'abstract': paper['abstract'],
            'citation_key': f"[{idx}]"
        })
    return references

async def generate_bibtex_entry(ref):
    """Generate BibTeX entry for a paper."""
    arxiv_id = ref['url'].split('/')[-1]
    bibtex = (
        f"@article{{{arxiv_id},\n"
        f"  author = {{{ref['authors']}}},\n"
        f"  title = {{{ref['title']}}},\n"
        f"  year = {{{ref['year']}}},\n"
        f"  eprint = {{{arxiv_id}}},\n"
        f"  archivePrefix = {{arXiv}},\n"
        f"  primaryClass = {{cs.LG}},\n"  # You might want to make this dynamic
        f"  url = {{{ref['url']}}}\n"
        f"}}\n\n"  # Added an extra newline after the BibTeX entry
    )
    return bibtex

async def generate_literature_review_async(session, user_query, paper_entries):
    """
    Generate literature review based on prepared references.
    """
    # First prepare all references
    references = await prepare_references(paper_entries)
    
    # Prepare paper information with citations
    papers_info = []
    for ref in references:
        papers_info.append(
            f"Paper {ref['citation_key']}:\n"
            f"Title: {ref['title']}\n"
            f"Abstract: {ref['abstract']}\n"
            f"Citation: Use {ref['citation_key']} to cite this paper"
        )

    # Generate Nature-style review
    review_prompt = (
        "Write a comprehensive literature review in Nature journal style. "
        "Requirements:\n"
        "1. Use formal Nature journal style\n"
        "2. Begin with a compelling introduction\n"
        "3. Organize findings into clear themes\n"
        "4. Use provided citation numbers [n] when discussing papers\n"
        "5. Each paper must be cited at least once\n"
        "6. Make connections between related papers\n"
        "7. Conclude with future directions\n"
        "7. Make sure the literature review is at least 6000 words if the {paper_count} are more than 70, and at least 4000 words when the {paper_count} are 40 to 70, andat least 2500 words when the {paper_count} are 10 to 39.\n"
        "8. DO NOT include references - they will be added separately\n"
        f"\nTopic: {user_query}\n\n"
        f"Available Papers:\n\n{chr(10).join(papers_info)}"
    )

    messages = [
        {"role": "system", "content": "You are a Nature journal editor writing a literature review."},
        {"role": "user", "content": review_prompt}
    ]
    
    literature_review = await call_openrouter_async(session, messages)

    if literature_review:
        # Format references in Nature style with clickable links
        refs_section = "\nReferences\n"
        bibtex_section = "\nBibTeX Citations:\n\n"  # New section for BibTeX

        for ref in references:
            arxiv_id = ref['url'].split('/')[-1]
            refs_section += (
                f"{ref['citation_number']}. {ref['authors']}. "
                f"{ref['title']}. "
                f"arXiv:{arxiv_id} ({ref['year']}). "
                f"Available at: {ref['url']}\n"
            )
            bibtex_section += await generate_bibtex_entry(ref)  # Generate BibTeX entry

        # Add section separator
        final_text = (
            literature_review +
            "\n" + "="*50 + "\n" +
            refs_section +
            "\n" + "="*50 + "\n" +  # Separator for BibTeX
            bibtex_section
        )

        return final_text

    return "Error generating literature review."

async def research_flow(user_query, paper_count):
    """
    Execute research flow with user-specified paper count.
    """
    async with aiohttp.ClientSession() as session:
        # Step 1: Get exact number of papers requested
        paper_entries = await search_arxiv_async(session, user_query, max_results=paper_count)
        
        if not paper_entries:
            return "No relevant papers found. Please try a different query."
        
        # Step 2: Generate review with prepared references
        literature_review = await generate_literature_review_async(session, user_query, paper_entries[:paper_count])
        return literature_review

# def main():
#     """CLI entry point."""
#     user_query = input("Enter your research topic/question: ").strip()
#     final_report = asyncio.run(research_flow(user_query))
#     print("\n==== LITERATURE REVIEW ====\n")
#     print(final_report)

# if __name__ == "__main__":
#     main()
