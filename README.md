# social-growth-automation

A Claude Code skill that builds automated engage-then-follow bots for Twitter/X and Instagram.

## What It Does

When you invoke this skill, Claude interactively walks you through:

1. Choosing a platform (Twitter/X or Instagram)
2. Defining your niche and competitor accounts
3. Setting up API credentials
4. Connecting Google Sheets for tracking
5. Generating a complete bot with scraping, warming, following, and unfollowing
6. Testing the full pipeline end-to-end

## Install

Copy the `social-growth-automation/` folder into your Claude Code skills directory:

```bash
cp -r social-growth-automation ~/.claude/skills/
```

Or for project-level use:

```bash
cp -r social-growth-automation .claude/skills/
```

## Usage

In Claude Code, just describe what you want:

- "I want to grow my Twitter following"
- "Set up an automated follow bot for Instagram"
- "Build an engage-then-follow workflow"

Claude will detect the skill and walk you through the interactive setup.

## Supported Platforms

| Platform | Method | Cost |
|----------|--------|------|
| Twitter/X | Twitter API v2 + Python scripts | ~$100/mo API |
| Instagram (API) | Python + instagrapi library | Free |
| Instagram (PhantomBuster) | PhantomBuster automation chain | ~$70-130/mo |

## Strategy Overview

The engage-then-follow strategy:

1. **Scrape** competitor followers (active, engaged users in your niche)
2. **Warm up** by liking 2-3 of their recent posts/tweets
3. **Follow** them hours later (they recognize your name from notifications)
4. **Unfollow** non-followers after 72 hours

This produces 10-20% follow-back rates vs 3-7% for cold following.

## File Structure

```
social-growth-automation/
  SKILL.md                        # Skill definition (Claude reads this)
  README.md                       # This file
  templates/
    twitter/                      # Twitter/X bot (API-based)
      config.py, sheets.py, scraper.py, warmer.py,
      follower.py, unfollower.py, runner.py,
      requirements.txt, .env.example
    instagram-api/                # Instagram bot (no PhantomBuster)
      config.py, sheets.py, scraper.py, warmer.py,
      follower.py, unfollower.py, runner.py,
      requirements.txt, .env.example
    instagram/                    # Instagram (PhantomBuster alternative)
      config.py, audit.py, check_today.py, deep_audit.py
```

## Requirements

- Python 3.9+
- **Twitter:** Twitter/X API access (developer.x.com) with Read+Write permissions
- **Instagram (API):** Just your Instagram username + password
- **Instagram (PhantomBuster):** PhantomBuster account ($70-130/mo)
- Google Cloud service account with Sheets API + Drive API enabled
- A Google Sheet shared with the service account

## Disclaimer

Automated following/unfollowing may violate platform Terms of Service. Use at your own risk.
