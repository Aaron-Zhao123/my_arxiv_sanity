import os
from paper_reader.notion import NotionDBManager

prefix = """
My primary research interest lies in enhancing the runtime efficiency of ML models, 
which encompasses areas such as quantization, pruning, and innovative compression techniques. 
Additionally, I am intrigued by AI system, AI hardware and AI safety research. 
Some of my previous research have included investigating efficient model serving systems, new AI hardware accelerators 
and red-teaming AI models, both of which are consistent with my interests. 
I am also keen to discover emerging models and learning paradigms to expand my knowledge base.
"""

database_id = os.environ["NOTION_DB_ID"]

db = NotionDBManager(database_id)
prompt = db.get_user_preference(prefix)
# execute daily
db.add_papers(prompt, past_days=7, max_papers=5)
