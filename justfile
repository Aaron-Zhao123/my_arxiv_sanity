install:
	uv pip install -r requirements.txt

format:
	black main.py
	black paper_reader/*

# this is to run local update of the preference.pkl and new_papers.pkl
local_update:
	python main.py
	git add new_papers.pkl
	git add preference.pkl
	git commit -m "Update new_papers and preference files"
	git push