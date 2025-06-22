# Quick setup guide

### Setups

1. Make sure you follow the guide [here](https://developers.notion.com/docs/create-a-notion-integration) to build a Notion integration.
2. Create a new database in Notion. The expected setup is to have the following entries:
	- TBD
3. Make sure the Notion database is shared with the integration you created in the next step.
4. Copy the database ID from the URL of the database page. It should look like this: `https://www.notion.so/<hash>?v=<hash2>`. The database ID `<database_id>` is the `<hash>` part.
5. Copy the integration token `<integration_token>` from the Notion integration page.
6. Make them available as environment variables:
	- `export NOTION_DB_ID=<database_id>`
	- `export NOTION_API_TOKEN=<integration_token>`
	- `export OPENAI_API_KEY=<integration_token>`
	- hint: you can add these to your `.bashrc` or `.zshrc` file to make them persistent across terminal sessions.

### Install dependencies
```bash
just install
```


### Run it once to test
```bash
python main.py
```
