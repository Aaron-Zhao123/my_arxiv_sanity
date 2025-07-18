# MyArxivSanity

An AI-powered arXiv paper recommendation system that intelligently discovers and curates research papers based on your preferences. The system uses GPT-4 to analyze paper abstracts, learns from your ratings in a Notion database, and generates beautiful static websites to showcase recommended papers.

## Key Features

- **Intelligent Paper Discovery**: Automatically searches arXiv for recent papers in ML/AI categories
- **Personalized Recommendations**: Uses GPT-4 to analyze and rank papers based on your learned preferences
- **Notion Integration**: Stores papers in a structured Notion database for easy tracking and review
- **Static Site Generation**: Creates responsive web interfaces for browsing recommendations
- **Automated Workflows**: Supports scheduled runs with automatic deployment to GitHub Pages
- **Multi-format Export**: Generates both JSON and Markdown outputs for flexible usage

## Quick Setup Guide

### Prerequisites

- Python 3.12+ with UV package manager
- [Just](https://github.com/casey/just) command runner
- OpenAI API key
- Notion workspace and integration

### Environment Setup

1. Make sure you follow the guide [here](https://developers.notion.com/docs/create-a-notion-integration) to build a Notion integration.
2. Create a new database in Notion. The expected setup is to have the following entries:
	- Name: Comes by default with the database.
	- Genre: A multi-select property to categorize the papers.
	- URL: A URL property to store the link to the paper.
	- Status: A multi-select property to indicate the status of the paper (e.g., "To Read", "Reading", "Finished").
	- Abstract: A text property to store the abstract of the paper.
	- Rating: A multi-select (1-5) property to store the rating of the paper, this is later used to construct the prompt for the LLM.
	- Review: A text property to store the review/notes of the paper.
	An example of the database can be found [here](https://www.notion.so/2177828c84588004b3d8d0ae2771d5e7?v=2177828c8458806db6b9000cdc6e47fe&source=copy_link).
3. Make sure the Notion database is shared with the integration you created in the next step, check the instructions [here](https://developers.notion.com/docs/create-a-notion-integration).
4. Copy the database ID from the URL of the database page. It should look like this: `https://www.notion.so/<hash>?v=<hash2>`. The database ID `<database_id>` is the `<hash>` part.
5. Copy the integration token `<integration_token>` from the Notion integration page.
6. Make them available as environment variables:
	- `export NOTION_DB_ID=<database_id>`
	- `export NOTION_API_TOKEN=<integration_token>`
	- `export OPENAI_API_KEY=<integration_token>`
	- hint: you can add these to your `.bashrc` or `.zshrc` file to make them persistent across terminal sessions.
7. Change the `prefix` variable in `main.py` to fit yourself.
8. Setup a `cron` job to run the script daily. You can use the following command to edit the crontab:

	```bash
	crontab -e
	```

	Add the following line to run the script every day at 11 AM:

	```bash
	0 11 * * * cd your_path/paper_reader && /opt/homebrew/bin/just local_update >> /tmp/paper_reader.log 2>&1
	```
	Notice `/opt/homebrew/bin/just` is the path to the `just` command.

### Usage

#### Run the Paper Recommendation System

```bash
# Run once to test
just run

# Or directly with python
python main.py
```

#### Export Papers to Static Site

```bash
# Export papers to markdown and JSON formats
python export_papers.py
```

#### Available Commands

- `just run`: Execute the main paper discovery and recommendation process
- `just local_update`: Run the system and automatically commit changes to pickle files

## Project Structure

```
paper_reader/
├── paper_reader/           # Core package
│   ├── paper.py           # Pydantic models for Paper and ListOfPapers
│   ├── notion.py          # Notion database integration
│   └── arxiv.py           # arXiv API client
├── docs/                  # Jekyll static site
│   ├── assets/           # CSS and other assets
│   │   └── css/
│   │       └── style.scss # Custom styling
│   ├── index.md          # Generated papers page
│   └── _config.yml       # Jekyll configuration
├── main.py               # Main entry point
├── export_papers.py      # Export utilities
├── local_update.py       # Local update script
├── justfile             # Build commands
├── new_paper.pkl        # Recently discovered papers
└── preference.pkl       # User preference profile
```

## How It Works

1. **Paper Discovery**: Searches arXiv for recent papers in ML/AI categories (cs.LG, cs.AI, cs.AR)
2. **Preference Learning**: Analyzes your ratings in the Notion database to build a preference profile
3. **Intelligent Ranking**: Uses GPT-4 to analyze paper abstracts and rank relevance based on your preferences
4. **Data Storage**: Stores new papers in the Notion database with structured metadata
5. **Static Site Generation**: Creates beautiful web interfaces for browsing recommendations
6. **Automated Deployment**: Supports GitHub Actions for automatic website updates

## Deployment

The project includes GitHub Actions workflow for automatic deployment to GitHub Pages. Papers are automatically exported to a Jekyll-based static site for easy browsing and sharing.
