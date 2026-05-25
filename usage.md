# JankLang — Usage

## Overview

JankLang is a tiny line-based scripting language implemented by `jank.py`. You can run a `.jank` script file or use the interactive REPL.

## Requirements

- Python 3.8+

## Run a script file

Run a JankLang file by passing its path to `jank.py`:

```bash
python jank.py path/to/script.jank
```

## Interactive REPL

Start the REPL with no arguments:

```bash
python jank.py
```

The prompt is `jank>` and supports multi-line `if` blocks terminated with `endif`.

## Language Reference

- Comments: lines starting with `#` are ignored.
- Commands:
  - `output <expr>` — evaluate `<expr>` and print the result.
  - `set <var> = <expr>` — assign the stringified result of `<expr>` to `<var>`.
  - `input <var> = <promptExpr>` — evaluate `<promptExpr>`, show it as prompt, store user input into `<var>`.
  - `exit` — quit the interpreter.
- Conditionals:
  - `if <condition>` ... `endif` — execute block when condition is true; `if` blocks may nest.
- Expressions:
  - `+` concatenates strings or adds numbers (mixed types become concatenation).
  - Strings use double quotes: `"hello"`.
  - Variables are referenced by name in expressions.
  - `tonumber(<expr>)` attempts to convert the inner expression to an int/float, returning `0` on failure.
- Conditions support `==`, `!=`, `<`, `>`, `<=`, `>=` and compare numeric values when possible.

## Examples

Simple output:

```jank
output "Hello, " + "World"
```

Variables and math:

```jank
set x = 1 + 2
output x
```

Input and condition:

```jank
input name = "Your name: "
if name == "Alice"
  output "Welcome back, Alice"
endif
```

## Notes

- Errors while processing a line are reported to stdout but do not crash the REPL.
- The interpreter treats values as strings by default; numeric operations occur when all operands parse as numbers.
