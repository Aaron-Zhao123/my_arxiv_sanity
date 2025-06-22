# What is this?

My Arxiv Sanity, a tool that recommends papers to read by crawling arxiv. How does it decide on the most relevant papers? It is powered by GPT...
Papers are fetched from arxiv, and then the script uses OpenAI's GPT to analyze the papers and recommend the most relevant ones based on your preferences.
These papers are then stored in a Notion database, which you can use to keep track of your reading list.

# Quick setup guide

### Setups

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
	0 11 * * * your/python/bin /path/to/your/script/main.py
	```

### Install dependencies

I assume you have an up-to-date Python version, and `justfile` installed. If not, you should install them first.

The rest of the dependencies can be installed using `just`:

```bash
just install
```


### Run it once to test

```bash
python main.py
```
