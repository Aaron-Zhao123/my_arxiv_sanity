# Paper Reader Frontend

This is the frontend for displaying new research papers from arXiv.

## Features

- Clean, responsive design
- Displays paper titles, authors, abstracts, and arXiv links
- Automatically updates when new papers are added
- Mobile-friendly interface

## Setup

The frontend is automatically deployed via GitHub Actions when:
- New papers are added (new_paper.pkl is updated)
- Changes are made to the frontend files
- Daily at 9 AM UTC (scheduled run)

## Files

- `index.html` - Main frontend page
- `papers.json` - JSON data file generated from new_paper.pkl
- `README.md` - This file

## Local Development

To test locally:
1. Run `python export_papers.py` to generate papers.json
2. Serve the docs folder with any static file server
3. Open index.html in your browser

## GitHub Pages

The site is automatically deployed to GitHub Pages at:
`https://[username].github.io/paper_reader/`

Make sure to enable GitHub Pages in your repository settings and set the source to "GitHub Actions".