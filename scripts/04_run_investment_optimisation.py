import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from aiml_mrms.data_utils import ensure_results_dirs
from aiml_mrms.investment import solve_by_country

tables_dir, _ = ensure_results_dirs()
topsis = pd.read_csv(tables_dir / "table7_topsis_results.csv")
allocations = solve_by_country(topsis, cycle=3, lambda_penalty=0.15)
allocations.to_csv(tables_dir / "investment_allocation_lambda_015.csv", index=False)
print("Investment optimisation complete.")
