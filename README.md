# Payment Processing: Raw Code vs. Skeleton

Practice files for the **M1B - Optimizing Technical Context** session. You will compare what it costs an AI to plan a refactor from the full code of a 15-file legacy payment module, against a compact **skeleton** of the same code.

## What's here

| File | Purpose |
|---|---|
| `payment_processing/` | The legacy payment module (15 Python files) |
| `1_count_tokens.py` | Counts the tokens of a file or folder |
| `2_make_skeleton.py` | Builds a skeleton: classes, method signatures, imports, first docstring line, no method bodies |
| `3_get_function.py` | Prints the full code of one function, for when you need raw code |

## Setup

You need Python 3.8 or later.

```
git clone https://github.com/dorinaamd/payment_processing
cd payment_processing
pip install tiktoken
```

`tiktoken` gives exact token counts. Without it, the counter falls back to a rough estimate (characters / 4) and the last line of its output says `ESTIMATE`. Make sure it says `tiktoken (cl100k_base)`.

## Step 1: Measure and compress

```
python 1_count_tokens.py payment_processing
python 2_make_skeleton.py payment_processing > skeleton.txt
python 1_count_tokens.py skeleton.txt
```

Write down both numbers. Your budget is 20% of the baseline (an 80% reduction).

## Step 2: Run the same task twice

Use a **new chat** for each run, in Agent mode, with the same model and settings, so the first answer does not stay in context.

**Run A: raw code.** Nothing attached:

```
The folder payment_processing contains 15 Python files of a legacy payment module. Read every file completely, from the first line to the last, one file at a time, in alphabetical order. Do not skip any file, do not use search or grep in place of reading, and do not stop at signatures.

Then answer: Which methods across these files handle validation? Group them by file and suggest what to extract into a new validation service. Flag anything you are unsure about.

Before your answer, list each file with the number of lines you read, so I can check nothing was skipped.
```

**Run B: skeleton.** Attach only `skeleton.txt`:

```
The attached skeleton.txt is a structural outline of the 15-file legacy payment module in the payment_processing folder: file names, imports, class names, method signatures and the first docstring line, with no method bodies. Use only this file and do not open or search any other file.

Then answer: Which methods across these files handle validation? Group them by file and suggest what to extract into a new validation service. Flag anything you are unsure about.
```

## Step 3: Compare

After each run, record the tokens and cost shown by your tool's context indicator.

| | Tokens | Cost | Found the same validation methods? |
|---|---|---|---|
| Run A (raw code) | | | |
| Run B (skeleton) | | | |

Then check the skeleton answer against the real code. The skeleton is good for planning, but anything the AI flags as uncertain needs the real code. To look at one function in full:

```
python 3_get_function.py payment_processing/order_service.py OrderService.process
```

**Rule of thumb:** use a skeleton to understand the system, use raw code to edit a specific function.
