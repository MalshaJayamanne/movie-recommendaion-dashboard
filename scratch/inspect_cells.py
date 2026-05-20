import json

notebook_path = r"backend/notebooks/moviemind.ipynb"
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
for i, cell in enumerate(cells):
    if cell.get('cell_type') == 'code' and 70 <= i <= 82:
        source = "".join(cell.get('source', []))
        print(f"Cell {i} Code:\n{source}\n")
