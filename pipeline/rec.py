"""rec.py E01 E01-S013 job1 job2 ... : record job ids in image_ledger.json (cost 2)."""
import sys; sys.path.insert(0,'.')
from pipeline import ledger
ep=sys.argv[1]; ids=sys.argv[2].split(','); jobs=sys.argv[3:]
for i,j in zip(ids,jobs): ledger.add(f"episodes/{ep}/image_ledger.json",i,job=j,attempt=2,cost=2)
print("recorded",len(jobs))
