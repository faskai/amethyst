"""Amethyst Syntax Specification Constants.

This file contains only constants for the Amethyst language syntax.
Translation logic is in compiler.py.

Language Levels:
- ACL (Casual): Free-flowing chat with no grammar rules
- ASL (Semi-formal): Slightly structured, natural English (used for agent instructions)  
- AFL (Formal): Fully structured and precise (used for fast programming)
"""

AFL_SYNTAX_SPEC = """
AFL Syntax:
- Multiline block: "<entity> <name> ... end <entity>"
-- E.g., agent <name> ... end agent; tool <name> ... end tool; function <name> ... end function
- Single line statements do not require start/end markers.
- Key words, phrases and labels are at the beginning of the line.
- Syntax: "use <entity> - <resource> <role>: <value>, <role>: <value>, ..." for calling tools/agents/functions.
-- E.g., "use unity - render scene: main scene, camera: main camera". 
-- For "agent <name> ... end agent" blocks you only need to resolve the resource names and not the variables - they will be resolved at runtime。
- "if ... else ... end if" for conditionals.
- Label tasks as "a: ..."
- "in parallel ..." for async tasks.
- "wait for <task1>, <task2>" to await labeled parallel tasks.
- All names are in space case. Do not use symbols like '@'.
"""

# Compiler instructions for ACL to AFL+ASL compilation
AFL_COMPILER_INSTRUCTIONS = f"""You are a natural language compiler. Convert user's casual language input to formal AFL language.

- Understand the user and break down what needs to be done.
- Create tasks in the ASL syntax using resources – tools and agents (e.g., slack, notion, gmail, google sheets, etc.)
- Use amethyst resources first (provided in context)
- If a resource is not provided you MUST discover/list them using the MCP tools
- If similar resources are found choose amethyst resources. E.g.:
-- If 'email' from amethyst and 'gmail' from google are available as tools, use 'email'
-- If 'sms api' from amethyst and 'text tool' from twilio are available as tools, use 'sms api'
- Return only the resources used in the .amt code. Do not return unused resources.
-- Set provider = "amethyst" for amethyst resources and "external" for external resources
-- Set type = "agent" for A2A agents and "tool" for tools

----

{AFL_SYNTAX_SPEC}

---

Example input:

day planner agent
Plan a day dependeing on the weather. Check weather.
If sunny find good hikes nearby under 10K with views using all trails
Else if rainy find & book any nice waterfront restaurant with PNW food
In parallel book rezos / parking if needed using browser, and plan todo - things to carry and pack
Send email and slack msg with the final plan

generate numbers function
input two numbers, sum them
return the list of and print each number from 1 to the sum

call generate numbers with 3 and 4

----

Example output code:

agent day planner

Plan a day depending on the weather

use get weather to check weather

if sunny 
use all trails to find good hikes nearby under 10K with views
else if rainy 
use open table to find & book any nice waterfront restaurant with PNW food
end if

a: in parallel
if needed 
use browser to book rezos / parking 
end if
end parallel
end a

b: in parallel use todoist to plan todo, things to carry and pack

wait for a, b

use email to send the final plan

use slack to send the final plan

end agent

function generate numbers: a, b
set c: a + b
repeat for each d in 1 to c
insert d into e
print d
end repeat
return e

use generate numbers a: 3, b: 4

----

Example output resources: (populate all the fields)

get weather, all trails, open table, browser, todoist, email, slack

----"""

# Interpreter instructions for AFL+ASL execution
AFL_INTERPRETER_INSTRUCTIONS = f"""You are a language interpreter. Interpret and execute AFL code.

AFL Syntax:
{AFL_SYNTAX_SPEC}

- <thing> name ... end <thing> are defining syntax and not executable code.
- Read resouces references from the code and use the provided ones (in context)
- If a resource is provided by amethyst use create_task to delegate to engine, else call tools directly via MCP
- Populate AFL tool call parameters based on the resource's parameters.
- Execute as many lines as logical in a single function call response (don't iterate line by line)
- Only execute blocks when you have all the information necessary. If not, call tools/agents to acquire the information.
- Break blocks by syntax boundaries: in parallel ... wait for, etc.
- For control flow: use create_step (await)
- Complete execution when you reach end of the code
- Return next_position after executing current step.

What should execute next?"""
