import zstandard as zstd
import json
from pathlib import Path

def peek_zst(filename, lines=5):
    filepath = Path(filename)
    if not filepath.exists():
        print(f"File {filename} not found.")
        return

    print(f"--- PEEKING INTO {filename} ---")
    dctx = zstd.ZstdDecompressor()
    with open(filepath, 'rb') as fh:
        # Use stream_reader to avoid loading everything
        with dctx.stream_reader(fh) as reader:
            # We need to read line by line from the decompressed stream
            import io
            text_stream = io.TextIOWrapper(reader, encoding='utf-8')
            for i, line in enumerate(text_stream):
                if i >= lines:
                    break
                try:
                    data = json.loads(line)
                    print(f"Line {i}: {json.dumps(data, indent=2)}")
                except Exception as e:
                    print(f"Error parsing line {i}: {e}")

if __name__ == "__main__":
    # Test with one submission and one comment file
    peek_zst("smallbusiness_submissions.zst", 1)
    peek_zst("smallbusiness_comments.zst", 1)
