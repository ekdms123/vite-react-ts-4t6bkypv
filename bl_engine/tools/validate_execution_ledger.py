from __future__ import annotations
from pathlib import Path
import sys, json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from stateful_author.executability import load_execution_ledger,load_claim_ledger,validate_execution_entries,validate_ledger_completeness,validate_claim_records,contract_coverage

def main()->int:
    entries=load_execution_ledger(ROOT/'verify/EXECUTION_LEDGER.json')
    claims=load_claim_ledger(ROOT/'verify/CLAIM_LEDGER.json')
    errors=validate_execution_entries(ROOT,entries)+validate_ledger_completeness(entries)+validate_claim_records(ROOT,claims)
    coverage=contract_coverage(ROOT,entries)
    print(json.dumps({'errors':errors,'coverage':coverage.to_dict()},ensure_ascii=False,indent=2,sort_keys=True))
    return 1 if errors or coverage.critical_executable!=coverage.critical_total else 0
if __name__=='__main__': raise SystemExit(main())
