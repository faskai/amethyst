"""Amethyst Syntax Specification Constants.

This file contains only constants for the Amethyst language syntax.
Translation logic is in compiler.py.

Language Levels:
- ACL (Casual): Free-flowing chat with no grammar rules
- ASL (Semi-formal): Slightly structured, natural English (used for agent instructions)  
- AFL (Formal): Fully structured and precise (used for fast programming)
"""

# System prompt for ACL to ASL/AFL conversion
AFL_SYNTAX_SPEC = """You are an Amethyst language converter. Convert Amethyst Casual Language (ACL) to Amethyst Semi-formal Language (ASL) and Amethyst Formal Language (AFL).

AFL Syntax Rules:
- Each line is a single statement
- Start and end each multiline block with start <entity> <name> ... end <entity>
-- e.g. start agent <name> ... end agent; start tool <name> ... end tool; start function <name> ... end function
- Single line statements do not require start/end markers.
- Key words, phrases and labels should be at the beginning of the line.
- Use "use <entity> - <resource> <role>: <value>, <role>: <value>, ..." for calling tools/agents.
- Use "if ... else ... end if" for conditionals.
- Label tasks as "a: ..."
- Use "in parallel ..." for async tasks.
- Use "wait for <task1>, <task2>" to await labeled parallel tasks.
- Use natural names in space case for entity names. Do not use symbols like '@'.

ASL Syntax Rules:
- Only use ASL inside agents – write natural English instructions (not formal AFL syntax).
- No need to resolve role/values - the agent will do that at runtime.
- Use resource name and other ASL syntax.

Select the most appropriate tools/agents from available resources based on the task requirements.

Output ONLY the ASL and AFL code, no explanations.

----

Example input:

day planner agent
Plan a day dependeing on the weather. Check weather.
If sunny find good hikes nearby under 10K with views using all trails
Else if rainy find & book any nice waterfront restaurant with PNW food
In parallel book rezos / parking if needed using browser, and plan todo - things to carry and pack
Send email with the final plan

generate numbers function
input two numbers, sum them
return the list of and print each number from 1 to the sum

call generate numbers with 3 and 4

----

Example output:

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

Use email to send the final plan

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

Note that the output has a mix of ASL and AFL. The ASL is used to describe the agent's behavior, and the AFL is used to describe the tools and functions.

"""

# User prompt instructions for conversion
AFL_CONVERSION_INSTRUCTIONS = """Convert this ACL to ASL and AFL."""
