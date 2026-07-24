import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from aiml_mrms.data_utils import project_root, ensure_results_dirs
from aiml_mrms.pci import compute_pci_table

tables_dir, _ = ensure_results_dirs()
root = project_root()
pci_input = pd.read_csv(root / "data" / "processed" / "pci_input_vectors.csv")
base = compute_pci_table(pci_input)
base.to_csv(tables_dir / "baseline_pci_rpci.csv", index=False)
print("PCI/RPCI complete.")
