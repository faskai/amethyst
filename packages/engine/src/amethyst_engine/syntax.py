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
1. Agents: "agent <name> ... end agent" blocks - extract name and full block
2. Functions: "function <name> ... end function" blocks

For functions, identify:
- Statements: "use <resource>" lines
- Repeats: "repeat for each in input ... end repeat" blocks

Return structured plan with amt_agents and functions.

Example:
{
  "amt_agents": [{"name": "bulk_summz", "block": "agent bulk_summz\nuse google_docs...\nend agent"}],
  "functions": [{
    "name": "doc_summz",
    "blocks": [{"type": "repeat", "statements": ["use google_docs to summarize"]}]
  }]
}

For sequences (not in repeat): {"type": "sequence", "statements": ["use x", "use y"]}
"""

AMT_INTERPRETER_INSTRUCTIONS = """Interpret Amethyst code and execute it.

Given code (agent block or single statement) and previous task results, execute it.

Rules:
- For an agent block you need to call resources to perform tasks.
- If resource is an AMT function: return task_type="amt_function_call", resource_name=function name, input as JSON array string
- If MCP tool executed: return task_type="statement_result", resource_name=tool name, result as text
- If agent block completed: return task_type="amt_agent_call", resource_name=agent name, result as final text
- Resolve variables from task results (e.g., "item" from current_item in context)
- Retry MCP tools if they fail, try different tools and parameters to get the desired result

Output format:
{
  "task_type": "amt_agent_call" | "amt_function_call" | "statement_result",
  "resource_name": "name of resource",
  "result": "text result (for amt_agent_call or statement_result)",
  "input": "[{\"key1\": \"val1\", \"key2\": \"val2\"}, {\"key1\": \"val3\", \"key2\": \"val4\"}]"
}

CRITICAL for amt_function_call input field:
- Must be a valid JSON array with NO extra text
- All objects in array must have identical keys (homogeneous structure)
- Example: [{"page": "doc1"}, {"page": "doc2"}] NOT [{"page": "doc1"}, {"list": ["x"]}]
"""
