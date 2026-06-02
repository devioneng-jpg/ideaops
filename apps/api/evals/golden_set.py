"""A small golden set of ideas for evaluating the specialist agents.

Each entry has a stable id, the raw idea text, and an optional `expect_category`
allow-list. We don't assert exact LLM output (it varies) — the runner checks that
every stage produces schema-valid output and that the few hard constraints hold.
"""

GOLDEN_IDEAS = [
    {
        "id": "job-postings-to-projects",
        "idea_text": (
            "An app that rewrites job postings into portfolio projects so job "
            "seekers can build exactly what employers are asking for."
        ),
        "expect_category": ["saas", "ai_agent", "content", "workflow_automation"],
    },
    {
        "id": "sql-from-natural-language",
        "idea_text": (
            "A CLI tool that turns natural language into SQL queries against your "
            "local Postgres database."
        ),
        "expect_category": ["ai_agent", "saas", "internal_tool"],
    },
    {
        "id": "standup-summarizer",
        "idea_text": (
            "An internal Slack bot that summarizes daily standup threads into a "
            "single digest for the engineering manager."
        ),
        "expect_category": ["internal_tool", "ai_agent", "workflow_automation"],
    },
    {
        "id": "freelance-marketplace",
        "idea_text": (
            "A marketplace connecting indie game developers with freelance pixel "
            "artists, with escrow payments and milestone tracking."
        ),
        "expect_category": ["marketplace", "saas"],
    },
    {
        "id": "newsletter-repurposer",
        "idea_text": (
            "A tool that turns a long-form newsletter into a week of tweets, a "
            "LinkedIn post, and a short video script."
        ),
        "expect_category": ["content", "ai_agent", "saas"],
    },
    {
        "id": "invoice-chaser",
        "idea_text": (
            "Software that automatically chases overdue invoices over email and "
            "SMS until a freelancer gets paid."
        ),
        "expect_category": ["workflow_automation", "saas"],
    },
    {
        "id": "habit-coach-agent",
        "idea_text": (
            "An AI accountability coach that texts you each morning, adapts to your "
            "goals, and nudges you when you fall behind."
        ),
        "expect_category": ["ai_agent", "saas"],
    },
    {
        "id": "receipt-expense-sorter",
        "idea_text": (
            "Snap a photo of a receipt and it categorizes the expense, extracts the "
            "total, and files it into the right spreadsheet."
        ),
        "expect_category": ["workflow_automation", "saas", "ai_agent"],
    },
    {
        "id": "open-source-changelog",
        "idea_text": (
            "A service that watches a GitHub repo and auto-generates a human-readable "
            "changelog and release notes from merged PRs."
        ),
        "expect_category": ["internal_tool", "ai_agent", "saas", "workflow_automation"],
    },
    {
        "id": "course-from-docs",
        "idea_text": (
            "Point it at any software documentation site and it generates an "
            "interactive mini-course with lessons and quizzes."
        ),
        "expect_category": ["content", "ai_agent", "saas"],
    },
]
