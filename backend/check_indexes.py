import warnings; warnings.filterwarnings("ignore")
import app.main
from app.db.session import Base, _dedupe_indexes
from collections import Counter
_dedupe_indexes(Base.metadata, None)
names = [i.name for t in Base.metadata.tables.values() for i in t.indexes if i.name]
dups = [n for n, c in Counter(names).items() if c > 1]
print("tables:", len(Base.metadata.tables), "indexes:", len(names))
print("DUPLICATE INDEX NAMES REMAINING:", dups if dups else "none")
