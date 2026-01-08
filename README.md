# Milestoner

An MCP server that helps developers share their build-in-public journey without context switching. It pulls context from git history and helps generate milestone updates for social platforms.

## What it does

When you hit a milestone while coding, ask your AI assistant to draft and post an update. Milestoner pulls your git context automatically and helps generate platform-appropriate content.

**Currently supported platforms:**
- Bluesky

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/J3r3my97/milestoner.git
cd milestoner

# Install with uv
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

## Configuration

### Claude Code

Add to your Claude Code MCP settings (`~/.claude/claude_desktop_config.json` or via Claude Code settings):

```json
{
  "mcpServers": {
    "milestoner": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/milestoner", "milestoner"]
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "milestoner": {
      "command": "milestoner"
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "milestoner": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/milestoner", "milestoner"]
    }
  }
}
```

## Setup

### 1. Create a Bluesky App Password

1. Go to [bsky.app/settings/app-passwords](https://bsky.app/settings/app-passwords)
2. Click "Add App Password"
3. Give it a name (e.g., "Milestoner")
4. Copy the generated password

### 2. Configure Milestoner

Ask your AI assistant:

> "Configure milestoner with my Bluesky account. My handle is yourname.bsky.social and my app password is xxxx-xxxx-xxxx-xxxx"

The assistant will use the `configure` tool to save your credentials securely.

## Usage

### See what you've been working on

> "What have I done this week that's worth posting about?"

The assistant will use `list_activity` to show your recent commits grouped by day.

### Draft an update

> "Draft a post about the authentication feature I just shipped"

The assistant will use `draft_update` to get git context, then generate a post for you to review.

### Post an update

> "Post that update to Bluesky"

The assistant will use `post_update` to publish your content and return a link to the live post.

### Schedule for optimal times

> "Schedule this post for the best time today"

The assistant will use `schedule_post` with `use_optimal_time: true` to queue your post for peak engagement (e.g., Wednesday 10 AM, weekday mornings).

### Check optimal posting times

> "When's the best time to post today?"

The assistant will use `get_optimal_times` to show you the best times based on engagement research.

## Tools

### `list_activity`

Shows recent git activity that could be posted about.

**Inputs:**
- `repo_path` (optional): Path to git repo. Defaults to current directory.
- `since` (optional): How far back to look. Defaults to "7 days".

### `draft_update`

Gets structured context for drafting a social media post.

**Inputs:**
- `context` (optional): What to focus on (e.g., "just shipped auth")
- `style` (optional): Tone - `casual`, `announcement`, `technical`, `storytelling`
- `repo_path` (optional): Path to git repo
- `commit_range` (optional): Specific commits (e.g., "abc123..def456" or "last 5")
- `platform` (optional): Target platform (defaults to configured default)

### `post_update`

Publishes content to a social platform.

**Inputs:**
- `content` (required): The content to post
- `platform` (optional): Target platform (defaults to configured default)

### `configure`

Sets up credentials for a platform.

**Inputs:**
- `platform` (required): Platform to configure (e.g., "bluesky")
- `handle`: Your handle on the platform
- `app_password`: App password for authentication
- `set_default` (optional): Set this as the default platform (default: true)

### `schedule_post`

Schedule a post for later at an optimal time.

**Inputs:**
- `content` (required): The content to post
- `scheduled_for` (optional): ISO datetime for when to post (e.g., "2025-01-15T10:00:00")
- `platform` (optional): Target platform (defaults to configured default)
- `use_optimal_time` (optional): Schedule for the next optimal posting time

### `list_scheduled_posts`

List all pending scheduled posts and upcoming optimal times.

### `cancel_scheduled_post`

Cancel a scheduled post.

**Inputs:**
- `post_id` (required): The ID of the scheduled post to cancel

### `get_optimal_times`

Get optimal posting times based on engagement research. Returns:
- Current time quality assessment
- Recommended posting times for today and tomorrow
- Best time this week (Wednesday 10 AM)
- Times to avoid

## Resources

### `milestoner://config`

Current configuration state and platform connection status.

### `milestoner://recent-posts`

History of posts made through Milestoner.

## Configuration Storage

Credentials are stored in `~/.milestoner/config.json` with restricted file permissions (600). Post history is stored in `~/.milestoner/post-history.json`.

## Adding New Platforms

Milestoner is designed to support multiple platforms. To add a new platform:

1. Create a new file in `src/milestoner/platforms/` (e.g., `twitter.py`)
2. Implement the `Platform` abstract base class
3. Add the platform to the registry in `src/milestoner/platforms/registry.py`

See `src/milestoner/platforms/bluesky.py` for an example implementation.

## License

MIT
