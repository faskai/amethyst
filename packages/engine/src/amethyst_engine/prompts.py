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

Given code (agent block or single statement) and previous task results, execute it.

Rules:
- For an agent block you need to call resources to perform tasks.
- Iterate with MCP tools internally to perform the tasks.
- Retry MCP tools if they fail, try different tools and parameters to get the desired result
- If resource is an AMT function: return task={resource_name, task_type="amt_function", input as JSON array string}
- If resource is an AMT agent: return task={resource_name, task_type="amt_agent", input as JSON array string}
- If MCP tool executed or agent/statement completed: return result={result text}
- Resolve variables from task results (e.g., "item" from input in context)

Output format (one of):
- For function call: {"task": {"resource_name": "function_name", "task_type": "amt_function", "input": "[{...}, {...}]"}}
- For agent call: {"task": {"resource_name": "agent_name", "task_type": "amt_agent", "input": "[{...}, {...}]"}}
- For completion: {"result": {"result": "final text"}}

CRITICAL:
- Do not use any amethyst resource that is not mentioned in the code.
- For function/agent call input field:
-- Must be a valid JSON array with NO extra text
-- All objects in array must have identical keys (homogeneous structure)
-- Example: [{"page": "doc1"}, {"page": "doc2"}] NOT [{"page": "doc1"}, {"list": ["x"]}]
"""
