import os
import json


from notion_client import Client
from openai import OpenAI
from .arxiv import (
    search_arxiv_abstract,
    search_arxiv_paper_info,
    get_recent_arxiv_papers,
)
from pydantic import BaseModel


class Paper(BaseModel):
    name: str
    arxiv_id: str
    summary: str
    authors: str


class ListOfPapers(BaseModel):
    papers: list[Paper]


class NotionDBManager:
    def __init__(self, database_id, gpt_model="gpt-4.1"):
        self.database_id = database_id
        self.notion = Client(auth=os.environ["NOTION_API_TOKEN"])
        self.oai = OpenAI()
        self.gpt_model = gpt_model
        self._read_paper_db(database_id)
        self.existing_notion_papers = self._get_all_db_papers()

    def add_papers(self, user_preference, past_days=7, max_papers=20):
        # add top ranked papers from arxiv to the notion database
        # the ranking is decided by gpt
        papers = get_recent_arxiv_papers(days_ago=past_days)
        sys_prompt = (
            "The user provided the following research interest description: "
            + user_preference
        )
        sys_prompt += f"Please return a list of papers (max {max_papers}) that are most relevant to the research interests based on the following papers:\n"

        print(
            f"Found {len(papers)} relevant papers from arxiv, from the past {past_days} days, filtering to {max_papers} most relevant papers."
        )

        prompt = "\n".join(
            [
                f"{paper['title']} by {paper['authors']} with the following summary {paper['summary']}, it has the following arxiv id {paper['id']}"
                for paper in papers
            ]
        )

        plain_response = self._gpt_query(sys_prompt + prompt)
        sys_prompt = "Extract the paper information."
        paper_list = self._gpt_query_formatted(
            sys_prompt=sys_prompt, prompt=plain_response, response_format=ListOfPapers
        )

        written = 0
        new_papers = []
        for p in paper_list.papers:
            # check whether the paper already exists in the database
            if not p.name in self.existing_notion_papers:
                self.write_paper_to_notion(p)
                new_papers.append(p)
                written += 1
        print(f"Added {written} papers to the notion database.")
        return new_papers

    def write_paper_to_notion(self, paper):
        # write a paper to the notion database
        # paper is a dict with keys: name, arxiv_id, summary
        print(paper.arxiv_id, paper.name, paper.summary)
        url = f"https://arxiv.org/abs/{paper.arxiv_id}" if paper.arxiv_id else None
        self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties={
                "Name": {"title": [{"text": {"content": paper.name}}]},
                "URL": {"url": url},
                "Abstract": {
                    "type": "rich_text",
                    "rich_text": [{"type": "text", "text": {"content": paper.summary}}],
                },
            },
        )

    def get_user_preference(self, prefix):
        positive_papers, negative_papers = {}, {}
        positive_papers = self._get_paper_by_ratings([4, 5])
        negative_papers = self._get_paper_by_ratings([1, 2])
        positive_papers = "\n".join(
            [f"{name}: {paper['abstract']}" for name, paper in positive_papers.items()]
        )
        negative_papers = "\n".join(
            [f"{name}: {paper['abstract']}" for name, paper in negative_papers.items()]
        )
        prompt = f"This is my general research interest: {prefix}\n\n"
        prompt += f"This is a list of papers I like (names and abstracts): {positive_papers}\n"
        prompt += f"This is a list of papers I do not like (names and abstracts): {negative_papers}\n"
        prompt += "(1) Please return a description of user research interests. (2) Add also a list of tags and keywords that best match the research interests based on the above papers the user liked and disliked.\n"
        return self._gpt_query(prompt)

    # --- DB operations ---
    def fill_empty_paper_abstract(self):
        # Fill empty paper abstracts with arxiv abstracts
        for paper in self.my_db["results"]:
            if not paper["properties"]["Abstract"]["rich_text"]:
                paper_title = paper["properties"]["Name"]["title"][0]["text"]["content"]
                print("Searching arxiv for abstract of paper:", paper_title)
                abstract = search_arxiv_abstract(paper_title, return_all=False)
                if abstract:
                    self.notion.pages.update(
                        page_id=paper["id"],
                        properties={
                            "Abstract": {"rich_text": [{"text": {"content": abstract}}]}
                        },
                    )
                    print("Updated abstract for paper:", paper_title)
                else:
                    print("No abstract found for paper:", paper_title)

    def fill_missing_url_and_abstract(self):
        """Scan all existing entries and add missing URL and abstract information"""
        print("Scanning database for missing URL and abstract information...")
        updated_count = 0

        for paper in self.my_db["results"]:
            paper_name = paper["properties"]["Name"]["title"][0]["text"]["content"]
            paper_id = paper["id"]

            # Check if URL is missing
            url_missing = not paper["properties"]["URL"]["url"]

            # Check if Abstract is missing
            abstract_missing = not paper["properties"]["Abstract"]["rich_text"]

            if url_missing or abstract_missing:
                print(f"Processing paper: {paper_name}")

                # Try to find paper on arxiv by title
                print(f"Searching arxiv for: {paper_name}")

                # Get paper info from arxiv
                paper_info = search_arxiv_paper_info(paper_name)

                # Update the paper if we found missing information
                update_properties = {}

                if paper_info:
                    if abstract_missing and paper_info.get("abstract"):
                        update_properties["Abstract"] = {
                            "rich_text": [{"text": {"content": paper_info["abstract"]}}]
                        }
                        print(f"Found abstract for: {paper_name}")

                    if url_missing and paper_info.get("url"):
                        update_properties["URL"] = {"url": paper_info["url"]}
                        print(f"Found URL for: {paper_name}")

                if update_properties:
                    self.notion.pages.update(
                        page_id=paper_id, properties=update_properties
                    )
                    updated_count += 1
                    print(f"Updated paper: {paper_name}")
                else:
                    print(f"No additional information found for: {paper_name}")

        print(f"Updated {updated_count} papers with missing information.")

    # --- helper functions ---

    def _gpt_query_formatted(self, sys_prompt, prompt, response_format=None):
        response = self.oai.responses.parse(
            model=self.gpt_model,
            input=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt},
            ],
            text_format=response_format,
        )
        return response.output_parsed

    def _gpt_function_calling_query(self, query, tools):
        response = self.oai.responses.create(
            model=self.gpt_model,
            input=[{"role": "user", "content": query}],
            tools=tools,
        )
        return response

    def _gpt_query(self, query):
        response = self.oai.responses.create(
            model=self.gpt_model,
            input=query,
        )
        return response.output_text

    def _read_paper_db(self, database_id):
        self.my_db = self.notion.databases.query(
            **{
                "database_id": database_id,
            }
        )

    def _get_paper_by_ratings(self, ratings):
        all_papers = self.existing_notion_papers
        selected_papers = {}
        for paper_name, paper_id in all_papers.items():
            page = self.notion.pages.retrieve(page_id=paper_id)
            abstract = (
                page["properties"]["Abstract"]["rich_text"][0]["text"]["content"]
                if page["properties"]["Abstract"]["rich_text"]
                else ""
            )
            # if rating exists
            if len(page["properties"]["Rating"]["multi_select"]) > 0:
                rating = int(page["properties"]["Rating"]["multi_select"][0]["name"])
                if rating in ratings:
                    selected_papers[paper_name] = {
                        "id": paper_id,
                        "abstract": abstract,
                        "rating": rating,
                    }
        return selected_papers

    def _get_all_db_papers(self):
        # parse contents to get a dict of paper names and ids
        paper_dict = {}
        for paper in self.my_db["results"]:
            paper_name = paper["properties"]["Name"]["title"][0]["text"]["content"]
            paper_id = paper["id"]
            paper_dict[paper_name] = paper_id
        return paper_dict
