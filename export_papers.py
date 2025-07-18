#!/usr/bin/env python3
"""
Script to convert new_paper.pkl to markdown format for static website.
"""

import pickle
import json
import os
import pydantic
from datetime import datetime
from typing import List, Dict, Any


def load_papers_from_pickle(pickle_file: str = "new_paper.pkl") -> List[Dict[str, Any]]:
    """Load papers from pickle file"""
    try:
        with open(pickle_file, 'rb') as f:
            papers = pickle.load(f)
        return papers
    except FileNotFoundError:
        print(f"Warning: {pickle_file} not found. No papers to export.")
        return []
    except Exception as e:
        print(f"Error loading {pickle_file}: {e}")
        return []


def convert_paper_to_dict(paper) -> Dict[str, Any]:
    """Convert paper object to dictionary"""
    try:
        # Handle both dict and object formats
        if hasattr(paper, 'name'):
            return {
                'name': paper.name,
                'arxiv_id': paper.arxiv_id,
                'summary': paper.summary,
                'authors': paper.authors
            }
        elif isinstance(paper, dict):
            return {
                'name': paper.get('name', ''),
                'arxiv_id': paper.get('arxiv_id', ''),
                'summary': paper.get('summary', ''),
                'authors': paper.get('authors', '')
            }
        else:
            print(f"Warning: Unknown paper format: {type(paper)}")
            return {
                'name': str(paper),
                'arxiv_id': '',
                'summary': '',
                'authors': ''
            }
    except Exception as e:
        print(f"Error converting paper: {e}")
        return {
            'name': 'Error loading paper',
            'arxiv_id': '',
            'summary': '',
            'authors': ''
        }


def export_to_markdown(papers: List[Any], output_file: str = "./index.md") -> None:
    """Export papers to markdown format"""
    try:
        # Convert papers to dict format
        papers_data = []
        for paper in papers:
            paper_dict = convert_paper_to_dict(paper)
            papers_data.append(paper_dict)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Generate markdown content
        markdown_content = f"""# 📚 MyArxivSanity

*Latest papers from arXiv based on your research interests*

<div class="stats">
<strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
<strong>Total Papers:</strong> {len(papers_data)}
</div>

---

"""
        
        if not papers_data:
            markdown_content += """
<div class="no-papers">
<h2>No New Papers Found</h2>
<p>Check back later for new research papers!</p>
</div>

---

*This page is automatically updated when new papers are added to your collection.*
"""
        else:
            for i, paper in enumerate(papers_data, 1):
                # Clean up the paper data
                title = paper.get('name', 'Unknown Title')
                authors = paper.get('authors', '')
                arxiv_id = paper.get('arxiv_id', '')
                summary = paper.get('summary', 'No summary available.')
                
                # Format authors
                authors_text = f"**Authors:** {authors}" if authors else ""
                
                # Format arXiv link
                arxiv_link = f'<a href="https://arxiv.org/abs/{arxiv_id}" class="arxiv-link">📄 View on arXiv</a>' if arxiv_id else ""
                
                markdown_content += f"""
## {i}. {title}

<div class="paper-meta">
{authors_text}
{arxiv_link}
</div>

### Abstract
<div class="abstract">
{summary}
</div>

---

"""
        
        # Write markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Exported {len(papers_data)} papers to {output_file}")
        
    except Exception as e:
        print(f"Error exporting to markdown: {e}")


def export_to_json(papers: List[Any], output_file: str = "docs/papers.json") -> None:
    """Export papers to JSON format (for compatibility)"""
    try:
        # Convert papers to dict format
        papers_data = []
        for paper in papers:
            paper_dict = convert_paper_to_dict(paper)
            papers_data.append(paper_dict)
        
        # Create output data
        output_data = {
            'papers': papers_data,
            'last_updated': datetime.now().isoformat(),
            'count': len(papers_data)
        }
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(papers_data)} papers to {output_file}")
        
    except Exception as e:
        print(f"Error exporting to JSON: {e}")


def main():
    """Main function"""
    print("Converting new_paper.pkl to markdown format...")
    
    # Load papers from pickle
    papers = load_papers_from_pickle()
    
    if not papers:
        print("No papers found, creating empty markdown file...")
        export_to_markdown([])
    else:
        print(f"Found {len(papers)} papers to export")
        export_to_markdown(papers)
    
    # Also export to JSON for compatibility
    export_to_json(papers)
    
    print("Export completed!")


if __name__ == "__main__":
    main()
