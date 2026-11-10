import os, sys, collections, argparse

# Change working directory to script's location to ensure consistent file paths
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def generate_prefix_tree(patterns):
    trie_children = [{}]
    next_node_id = 1
    output_lines = []
    for pattern in patterns:
        node = 0
        for ch in pattern:
            if ch in trie_children[node]:
                node = trie_children[node][ch]
            else:
                trie_children[node][ch] = next_node_id
                trie_children.append({})
                output_lines.append(f"{node}->{next_node_id}:{ch}")
                node = next_node_id
                next_node_id += 1
    return trie_children, output_lines

def entering(text, patterns):
    trie_children, output_lines = generate_prefix_tree(patterns)
    pattern_outputs = [[] for _ in range(len(trie_children))]
    for pid, pat in enumerate(patterns):
        node = 0
        for ch in pat:
            node = trie_children[node][ch]
        pattern_outputs[node].append(pid)
    fail = [0] * len(trie_children)
    queue = collections.deque()
    for ch, child in trie_children[0].items():
        fail[child] = 0
        queue.append(child)
    while queue:
        node = queue.popleft()
        for ch, child in trie_children[node].items():
            queue.append(child)
            f = fail[node]
            while f and ch not in trie_children[f]:
                f = fail[f]
            fail[child] = trie_children[f].get(ch, 0)
            pattern_outputs[child].extend(pattern_outputs[fail[child]])
    node = 0
    result_set = set()
    for i, ch in enumerate(text):
        while node and ch not in trie_children[node]:
            node = fail[node]
        node = trie_children[node].get(ch, 0)
        for pat_id in pattern_outputs[node]:
            start = i - len(patterns[pat_id]) + 1
            if start >= 0:
                result_set.add(start)
    result = sorted(result_set)
    if result:
        output_lines.append(" ".join(map(str, result)))
    return output_lines

def main():
    parser = argparse.ArgumentParser(description="Prefix Tree Tasks Runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--task1", action="store_true", help="Run Task 1: Build prefix tree from patterns")
    group.add_argument("--task2", action="store_true", help="Run Task 2: Find pattern occurrences in text")
    args = parser.parse_args()

    # Read input data from input.dat file or from standard input
    try:
        with open("input.dat", "r") as f:
            raw_lines = f.read().splitlines()
    except FileNotFoundError:
        raw_lines = sys.stdin.read().splitlines()
    data = [line.strip() for line in raw_lines if line.strip()]

    # Prepare output lines based on chosen task
    output_lines_to_write = []
    if not data:
        # If no input data, create an empty output file
        output_lines_to_write = []
    else:
        if args.task1:
            # Task 1 input format: first line is number of patterns, subsequent lines are patterns
            try:
                # First line might be an integer count (we don't necessarily need to use it)
                _ = int(data[0])
                patterns = data[1:]
            except ValueError:
                # If first line is not an integer, treat entire file as patterns list
                patterns = data
            _, output_lines = generate_prefix_tree(patterns)
            output_lines_to_write = output_lines
        elif args.task2:
            # Task 2 input format: first line is text, second line is number of patterns, then patterns
            text = data[0]
            try:
                _ = int(data[1])
                patterns = data[2:]
            except (ValueError, IndexError):
                # If second line missing or not an integer, assume all lines after text are patterns
                patterns = data[1:]
            output_lines = entering(text, patterns)
            # Only output the indices line (omit prefix tree edges in output file)
            if output_lines and "->" not in output_lines[-1]:
                # The last line is the result line with indices
                output_lines_to_write = [output_lines[-1]]
            else:
                # No occurrences found, output should be empty
                output_lines_to_write = []

    with open("output.dat", "w") as fout:
        for line in output_lines_to_write:
            fout.write(line + "\n")

if __name__ == "__main__":
    main()
