"""Amethyst Syntax Specification Constants.

This file contains only constants for the Amethyst language syntax.
Translation logic is in compiler.py.
"""

AMT_SYNTAX_SPEC = """
Amethyst Syntax:
- Multiline block: "<entity> <name> ... end <entity>"
-- E.g., agent <name> ... end agent; tool <name> ... end tool; function <name> ... end function
- Single statements do not require start/end markers.
-- E.g., "use <entity> - <resource> <role>: <value>, <role>: <value> to do xyz".
- Key words, phrases and labels are at the beginning of the line.
- Syntax: "use <entity> - <resource> <role>: <value>, <role>: <value>, ..." for calling tools/agents/functions.
-- E.g., "use unity - render scene: main scene, camera: main camera". 
-- For "agent <name> ... end agent" blocks you only need to resolve the resource names and not the variables - they will be resolved at runtime。
- "if ... else ... end if" for conditionals.
- Label tasks as "a: ..."
- "in parallel ..." for async tasks.
- "wait for <task1>, <task2>" to await labeled parallel tasks.
- Do not use symbols like '@' before resource names.
"""

AMT_PARSER_INSTRUCTIONS = """Parse Amethyst code into structured execution plan.

Identify:
1. Agents: "agent <name> ... end agent" blocks - extract name, type, and full code block
2. Functions: "function <name> ... end function" blocks - extract name, type, and execution blocks
3. Main entry point: "main agent <name>" or "main function <name>" - mark resource with is_main: true

For agents:
- Set type: "amt_agent"
- Extract full code in "code" field (the entire agent block content)
- blocks: [] (agents don't have structured blocks, just code)

For functions:
- Set type: "amt_function"
- Extract execution blocks with statements
- Statements: {"text": "use <resource>", "is_parallel": false}
- Parallel statements: {"text": "parallel use <resource>", "is_parallel": true}
- Repeats: {"type": "repeat", "statements": [...]}
- Wait: {"type": "wait", "statements": []}
- Sequences: {"type": "sequence", "statements": [...]}

Return as ResourceExpanded array:

{
  "resources": [
    {
      "name": "bulk_summz",
      "type": "amt_agent",
      "provider": "amethyst",
      "is_main": true,
      "code": "use google_docs to list files\nuse doc_summz to process",
      "blocks": []
    },
    {
      "name": "doc_summz",
      "type": "amt_function",
      "provider": "amethyst",
      "is_main": false,
      "blocks": [
        {
          "type": "repeat",
          "statements": [
            {"text": "use google_docs to summarize", "is_parallel": false}
          ]
        },
        {"type": "wait", "statements": []}
      ]
    }
  ]
}
"""

AMT_INTERPRETER_INSTRUCTIONS = """Interpret Amethyst code and execute it.

Given code (agent block or single statement), execute it using MCP tools and Amethyst resources.

Rules:
- Use MCP tools to perform tasks (e.g., google_docs, file operations)
- Iterate with MCP tools internally - retry if they fail with different parameters
- When you need to call an Amethyst function or agent, use the call_amt_resource function
- After calling call_amt_resource, the result will be provided and you can continue
- When task is complete, respond with the final result text as a regular message

To call Amethyst resources:
- Use call_amt_resource function with resource_name, task_type, and input
- task_type: "amt_function" or "amt_agent"
- input: ALWAYS provide this field as an array of objects
  - If no input needed, use empty array: []
  - Otherwise: [{"page": "doc1"}, {"page": "doc2"}]
  - All objects must have identical keys

CRITICAL:
- Only call Amethyst resources that are explicitly mentioned in the code
- ALWAYS include the input field, even if empty array []
"""
