install:
	uv pip install -r requirements.txt

format:
	black main.py
	black paper_reader/*