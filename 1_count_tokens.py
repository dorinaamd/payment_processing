"""Step 1 & 3: count the tokens in a folder (or a single file).

Usage:  python 1_count_tokens.py payment_processing
        python 1_count_tokens.py skeleton.txt
"""
import sys
from pathlib import Path

try:
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    count = lambda text: len(enc.encode(text))
    method = "tiktoken (cl100k_base)"
except ImportError:  # offline fallback so the demo still runs
    count = lambda text: len(text) // 4
    method = "ESTIMATE (characters / 4) - install tiktoken for exact counts"

target = Path(sys.argv[1])
files = sorted(target.rglob("*.py")) if target.is_dir() else [target]

total = 0
for f in files:
    n = count(f.read_text())
    total += n
    print(f"{n:>8,}  {f.name}")
print(f"{'-' * 8}\n{total:>8,}  TOTAL tokens   [{method}]")
