import json

notebook_path = r"backend/notebooks/moviemind.ipynb"
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
print(f"Total cells: {len(cells)}")

for i, cell in enumerate(cells):
    cell_type = cell.get('cell_type')
    source = "".join(cell.get('source', []))
    if cell_type == 'markdown' and ('model' in source.lower() or 'feature' in source.lower() or 'recommend' in source.lower() or 'similarity' in source.lower() or 'vector' in source.lower()):
        print(f"\n--- Cell {i} (Markdown) ---")
        print(source.strip())
    elif cell_type == 'code' and i >= 50:
        print(f"\n--- Cell {i} (Code) ---")
        print(source.strip())
