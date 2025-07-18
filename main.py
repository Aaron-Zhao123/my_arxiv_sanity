import os
import argparse
import pickle
from paper_reader.notion import NotionDBManager

prefix = """
My primary research interest lies in enhancing the runtime efficiency of ML models, 
which encompasses areas such as quantization, pruning, and innovative compression techniques. 
Additionally, I am intrigued by AI system, AI hardware and AI safety research. 
Some of my previous research have included investigating efficient model serving systems, new AI hardware accelerators 
and red-teaming AI models, both of which are consistent with my interests. 
I am also keen to discover emerging models and learning paradigms to expand my knowledge base.
"""

def generate_preference(db, prefix, output_file="preference.pkl"):
    """Generate user preference and save to pickle file"""
    print("Generating user preference...")
    prompt = db.get_user_preference(prefix)
    with open(output_file, 'wb') as f:
        pickle.dump(prompt, f)
    print(f"Preference saved to {output_file}")
    return prompt

def load_preference(file_path="preference.pkl"):
    """Load user preference from pickle file"""
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Preference file {file_path} not found. Please generate it first.")
        return None

def save_new_papers(new_papers, output_file="new_paper.pkl"):
    """Save new papers to pickle file"""
    if new_papers:
        with open(output_file, 'wb') as f:
            pickle.dump(new_papers, f)
        print(f"Saved {len(new_papers)} new papers to {output_file}")
    else:
        print("No new papers to save.")

def main():
    parser = argparse.ArgumentParser(description='Paper Reader CLI')
    parser.add_argument('--generate-preference', action='store_true', 
                       help='Generate preference.pkl file')
    parser.add_argument('--refresh-preference', action='store_true',
                       help='Refresh/regenerate preference.pkl file')
    parser.add_argument('--add-papers', action='store_true',
                       help='Add papers to Notion database')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of past days to search papers (default: 7)')
    parser.add_argument('--max-papers', type=int, default=10,
                       help='Maximum number of papers to add (default: 5)')
    parser.add_argument('--preference-file', type=str, default='preference.pkl',
                       help='Path to preference file (default: preference.pkl)')
    
    args = parser.parse_args()
    
    database_id = os.environ["NOTION_DB_ID"]
    db = NotionDBManager(database_id)
    
    if args.generate_preference or args.refresh_preference:
        generate_preference(db, prefix, args.preference_file)
    
    if args.add_papers:
        prompt = load_preference(args.preference_file)
        if prompt:
            new_papers = db.add_papers(prompt, past_days=args.days, max_papers=args.max_papers)
            save_new_papers(new_papers)
    
    # If no arguments provided, run default behavior, house keeping daily runs
    if not any([args.generate_preference, args.refresh_preference, args.add_papers]):
        prompt = load_preference(args.preference_file)
        if not prompt:
            prompt = generate_preference(db, prefix, args.preference_file)
        new_papers = db.add_papers(prompt, past_days=args.days, max_papers=args.max_papers)
        save_new_papers(new_papers)

if __name__ == "__main__":
    main()
