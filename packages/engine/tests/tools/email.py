#!/usr/bin/env python3
"""Email tool implementation for Amethyst testing."""

import mcp.types as types
from typing import Any


def email_tool(recipient: str = "user@example.com", subject: str = "Day Plan", content: str = "No content provided") -> str:
    """Send an email."""
    return f"""
📧 **Email Sent Successfully:**
- To: {recipient}
- Subject: {subject}
- Content: {content}
- Status: ✅ Delivered
- Sent at: Just now
    """.strip()


# Tool metadata for MCP protocol
TOOL_INFO = {
    "name": "email",
    "description": "Send an email with specified content", 
    "function": email_tool,
    "parameters": {
        "recipient": {
            "type": "string", 
            "description": "Email recipient", 
            "default": "user@example.com"
        },
        "subject": {
            "type": "string", 
            "description": "Email subject", 
            "default": "Day Plan"
        },
        "content": {
            "type": "string", 
            "description": "Email content", 
            "default": "No content provided"
        }
    },
    "mcp_schema": {
        "type": "object", 
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Email recipient address"
            },
            "subject": {
                "type": "string", 
                "description": "Email subject line"
            },
            "content": {
                "type": "string",
                "description": "Email content/body"
            }
        },
        "required": ["recipient", "subject", "content"]
    }
}


async def handle_mcp_call(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle MCP tool call for email."""
    recipient = arguments.get("recipient", "user@example.com")
    subject = arguments.get("subject", "Day Plan")
    content = arguments.get("content", "No content provided")
    
    email_response = f"""
📧 **Email Sent Successfully:**

**📬 Details:**
- To: {recipient}
- Subject: {subject}
- Status: ✅ Delivered
- Sent at: Just now
- Message ID: msg_20241201_{hash(content) % 10000:04d}

**📝 Content Preview:**
{content[:200]}{'...' if len(content) > 200 else ''}

**✅ Delivery confirmed to recipient's inbox**
    """
    
    return [types.TextContent(type="text", text=email_response.strip())]
