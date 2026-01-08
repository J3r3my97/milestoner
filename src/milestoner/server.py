import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from .config.store import get_post_history
from .platforms.registry import list_platforms
from .tools.configure import configure, get_configuration_status
from .tools.draft_update import draft_update
from .tools.list_activity import list_activity
from .tools.post_update import post_update

server = Server("milestoner")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_activity",
            description="Show recent git activity that could be posted about",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repo (defaults to current directory)",
                    },
                    "since": {
                        "type": "string",
                        "description": "How far back to look (e.g., '7 days', '2 weeks')",
                        "default": "7 days",
                    },
                },
            },
        ),
        Tool(
            name="draft_update",
            description="Get structured context for drafting a social media post from git activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "What to focus on (e.g., 'just shipped auth')",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["casual", "announcement", "technical", "storytelling"],
                        "description": "Tone of the post",
                        "default": "casual",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repo (defaults to current directory)",
                    },
                    "commit_range": {
                        "type": "string",
                        "description": "Specific commits (e.g., 'abc123..def456' or 'last 5')",
                    },
                    "platform": {
                        "type": "string",
                        "description": f"Target platform ({', '.join(list_platforms())})",
                    },
                },
            },
        ),
        Tool(
            name="post_update",
            description="Publish content to a social platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to post",
                    },
                    "platform": {
                        "type": "string",
                        "description": f"Target platform ({', '.join(list_platforms())})",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="configure",
            description="Set up credentials for a social platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": f"Platform to configure ({', '.join(list_platforms())})",
                    },
                    "handle": {
                        "type": "string",
                        "description": "Your handle on the platform",
                    },
                    "app_password": {
                        "type": "string",
                        "description": "App password (create at bsky.app/settings/app-passwords)",
                    },
                    "set_default": {
                        "type": "boolean",
                        "description": "Set this as the default platform",
                        "default": True,
                    },
                },
                "required": ["platform"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "list_activity":
        result = list_activity(
            repo_path=arguments.get("repo_path"),
            since=arguments.get("since", "7 days"),
        )
    elif name == "draft_update":
        result = draft_update(
            context=arguments.get("context"),
            style=arguments.get("style", "casual"),
            repo_path=arguments.get("repo_path"),
            commit_range=arguments.get("commit_range"),
            platform=arguments.get("platform"),
        )
    elif name == "post_update":
        result = post_update(
            content=arguments["content"],
            platform=arguments.get("platform"),
        )
    elif name == "configure":
        # Extract credentials from arguments
        platform = arguments["platform"]
        set_default = arguments.get("set_default", True)
        credentials = {k: v for k, v in arguments.items() if k not in ["platform", "set_default"]}
        result = configure(platform=platform, set_default=set_default, **credentials)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="milestoner://config",
            name="Milestoner Configuration",
            description="Current configuration state and platform connection status",
            mimeType="application/json",
        ),
        Resource(
            uri="milestoner://recent-posts",
            name="Recent Posts",
            description="History of posts made through Milestoner",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "milestoner://config":
        status = get_configuration_status()
        return json.dumps(status, indent=2)
    elif uri == "milestoner://recent-posts":
        history = get_post_history()
        return json.dumps({"posts": history}, indent=2)
    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})


def main():
    """Run the MCP server."""
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
