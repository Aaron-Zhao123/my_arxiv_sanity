from pydantic import BaseModel


class Paper(BaseModel):
    name: str
    arxiv_id: str
    summary: str
    authors: str


class ListOfPapers(BaseModel):
    papers: list[Paper]
