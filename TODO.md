# TODO

## Findings

### Medium: Output format is ambiguous for filenames containing newlines or control characters

- Problem: file paths are interpolated directly into diagnostics and result lines without escaping.
- Impact: a filename containing `\n`, `\r`, tabs, or other control characters can make one file look like multiple output records, which is unsafe for scripts and confusing for humans.
- Evidence: [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L69), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L77), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L79), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L81), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L89), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L99), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L119), [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L122)
- Reproduction: a file named `weird\nname.txt` produces a multi-line record on stdout.
- Recommended fix: escape filenames in human-readable output or add a machine-safe mode such as NUL-delimited or JSON output.

### Low: Documented target-set rule can drift from the implementation

- Problem: the docs describe the target set as “all characters matched by `str.isspace()` except ASCII space, tab, and LF, plus a few extra invisibles”, but the implementation is a hand-maintained regex.
- Impact: future Unicode or Python behavior changes can make the code and docs diverge silently.
- Evidence: [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L17), [README.md](/home/moriwaka/Src/nospc/README.md#L21), [nospc.1](/home/moriwaka/Src/nospc/nospc.1#L17)
- Recommended fix: derive the matcher from a predicate based on `str.isspace()`, or add a regression test that asserts the regex stays aligned with the documented rule.

### Low: High-match lines are built with repeated string concatenation

- Problem: `highlight_non_standard_whitespace()` appends to a Python string inside the match loop.
- Impact: large lines with many matches will do more copying than necessary.
- Evidence: [nospc.py](/home/moriwaka/Src/nospc/nospc.py#L40)
- Recommended fix: accumulate chunks in a list and `''.join()` them at the end.

## Open Questions / Assumptions

- This review assumes the current human-readable output format is intended to be stable. If machine-safe output is a goal, the filename-escaping issue should be prioritized higher.
- I treated the current `pytest` suite as the intended behavioral contract and focused the review on runtime edge cases and doc drift outside that coverage.

## Coverage Gaps

- No test covers filenames containing control characters or embedded newlines.
- No test checks that the regex stays aligned with the documented `str.isspace()`-based rule.

## Optional Next Steps

- Add a small output-formatting helper for filenames and route every stdout/stderr path through it.
- Add a target-set consistency test so future edits cannot drift from the documented rule unnoticed.
