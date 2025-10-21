"""Amethyst compiler for ACL to ASL+AFL conversion.

Language Levels:
- ACL (Casual): Free-flowing chat with no grammar rules
- ASL (Semi-formal): Slightly structured, natural English (used for agent instructions)
- AFL (Formal): Fully structured and precise (used for fast programming)
"""

import openai
from typing import List
from .syntax import AFL_SYNTAX_SPEC, AFL_CONVERSION_INSTRUCTIONS


def get_system_prompt(tool_list: str, agent_list: str) -> str:
    """Generate system prompt for ACL to AFL conversion."""
    return f"""{AFL_SYNTAX_SPEC}

Available Resources:
- Tools: {tool_list}
- Agents: {agent_list}"""


def get_user_prompt(acl_text: str) -> str:
    """Generate user prompt for ACL to AFL conversion."""
    return f"""{AFL_CONVERSION_INSTRUCTIONS}

ACL Input:
{acl_text}"""


async def convert_acl_to_afl(
    client: openai.OpenAI,
    acl_text: str, 
    available_resources: List[str]
) -> str:
    """Convert Amethyst Casual Language (ACL) to Amethyst Formal Language (AFL)."""
    
    tools = [r for r in available_resources if r.startswith('tool:')]
    agents = [r for r in available_resources if r.startswith('agent:')]
    
    tool_list = ', '.join([t[5:] for t in tools]) if tools else "None"
    agent_list = ', '.join([a[6:] for a in agents]) if agents else "None"
    
    # Use centralized prompts
    system_prompt = get_system_prompt(tool_list, agent_list)
    user_prompt = get_user_prompt(acl_text)

    try:
        print("🔄 Calling GPT to convert ACL to AFL...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        afl_code = response.choices[0].message.content.strip()
        
        print("\n✅ AFL Generated:")
        print("-" * 60)
        print(afl_code)
        print("-" * 60)
        
        return afl_code
        
    except Exception as e:
        raise Exception(f"ACL to AFL conversion failed: {e}")

