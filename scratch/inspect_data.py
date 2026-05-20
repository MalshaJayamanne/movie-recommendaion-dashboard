import pandas as pd
import json
import os

print("--- Checking CSV Files ---")
movies_path = r"backend/data/movies.csv"
credits_path = r"backend/data/credits.csv"

if os.path.exists(movies_path):
    df_movies = pd.read_csv(movies_path, nrows=5)
    print("Movies CSV columns:", df_movies.columns.tolist())
    print("Movies Sample:\n", df_movies.head(2))
else:
    print("Movies CSV not found!")

if os.path.exists(credits_path):
    df_credits = pd.read_csv(credits_path, nrows=5)
    print("Credits CSV columns:", df_credits.columns.tolist())
    print("Credits Sample:\n", df_credits.head(2))
else:
    print("Credits CSV not found!")

notebook_path = r"backend/notebooks/moviemind.ipynb"
if os.path.exists(notebook_path):
    print("\n--- Reading Notebook structure ---")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        cells = nb.get('cells', [])
        print(f"Number of cells in notebook: {len(cells)}")
        
        # Print first few code cells or titles
        code_cell_count = 0
        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type')
            source = "".join(cell.get('source', []))
            if cell_type == 'markdown' and len(source.strip()) > 0:
                print(f"Cell {i} (Markdown): {source.strip()[:100]}...")
            elif cell_type == 'code':
                code_cell_count += 1
                if code_cell_count <= 8:
                    print(f"Cell {i} (Code - {code_cell_count}):\n{source.strip()[:200]}\n")
