run:
	uv run python main.py
format:
	black main.py
	black paper_reader/*

# this is to run local update of the preference.pkl and new_papers.pkl
local_update:
	uv run python main.py
	@if git diff --quiet new_paper.pkl preference.pkl 2>/dev/null; then \
		echo "No changes to pickle files, skipping git push"; \
	else \
		echo "Changes detected in pickle files, committing and pushing"; \
		git add new_paper.pkl preference.pkl; \
		git commit -m "Update new_papers and preference files"; \
		git push; \
	fi