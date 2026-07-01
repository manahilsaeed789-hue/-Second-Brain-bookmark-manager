"""AI summarization and tag generation with OpenAI + local fallbacks."""

import json
import re
from typing import Optional

from backend.config import get_settings

settings = get_settings()


def _local_summarize(title: str, content: str) -> dict:
    """Rule-based fallback when OpenAI is unavailable."""
    sentences = re.split(r"(?<=[.!?])\s+", content.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    short = " ".join(sentences[:2]) if sentences else f"Saved content: {title}"
    if len(short) > 300:
        short = short[:297] + "..."

    detailed = " ".join(sentences[:6]) if sentences else content[:800]
    if len(detailed) > 1200:
        detailed = detailed[:1197] + "..."

    # Extract key phrases as pseudo-insights
    words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content[:3000])
    unique_phrases = list(dict.fromkeys(words))[:5]
    insights = unique_phrases[:4] if unique_phrases else [
        f"Content covers topics related to {title}",
        "Review the full text for detailed information",
    ]

    takeaways = [
        "Revisit this content when working on related projects",
        "Consider adding personal notes to reinforce learning",
    ]

    return {
        "short_summary": short,
        "detailed_summary": detailed,
        "key_insights": insights,
        "actionable_takeaways": takeaways,
    }


def _local_tags(title: str, content: str) -> dict:
    """Generate tags using keyword extraction heuristics."""
    text = f"{title} {content}".lower()

    topic_keywords = {
        "AI": ["artificial intelligence", "machine learning", "neural", "deep learning", "llm", "gpt", "transformer"],
        "Machine Learning": ["machine learning", "model training", "dataset", "classification", "regression"],
        "Programming": ["python", "javascript", "code", "api", "function", "programming", "developer"],
        "Research": ["study", "research", "paper", "hypothesis", "experiment", "analysis"],
        "Productivity": ["productivity", "focus", "habit", "workflow", "time management", "efficiency"],
        "Career": ["career", "job", "interview", "resume", "salary", "professional"],
        "Tutorial": ["tutorial", "how to", "step by step", "guide", "learn"],
        "Design": ["design", "ui", "ux", "interface", "visual"],
        "Data Science": ["data science", "pandas", "numpy", "visualization", "statistics"],
        "Web Development": ["html", "css", "react", "frontend", "backend", "web"],
    }

    category_map = {
        "Research": ["research", "paper", "study", "academic"],
        "Career": ["career", "job", "interview"],
        "Tutorials": ["tutorial", "how to", "guide", "learn"],
        "Exams": ["exam", "test", "quiz", "certification"],
        "Personal Growth": ["growth", "mindset", "habit", "self-improvement", "productivity"],
    }

    intent_keywords = {
        "Reference": ["reference", "documentation", "api"],
        "Learning": ["learn", "tutorial", "course", "study"],
        "Implementation": ["implement", "build", "create", "code"],
        "Inspiration": ["inspiration", "idea", "creative"],
    }

    learning_keywords = {
        "Beginner": ["introduction", "beginner", "basics", "getting started"],
        "Intermediate": ["intermediate", "advanced concepts"],
        "Advanced": ["advanced", "expert", "deep dive", "architecture"],
    }

    def match_tags(keyword_map: dict, tag_type: str) -> list[str]:
        matched = []
        for tag, keywords in keyword_map.items():
            if any(kw in text for kw in keywords):
                matched.append(tag)
        if not matched and tag_type == "topic":
            # Extract capitalized terms as topics
            caps = re.findall(r"\b[A-Z][a-z]{3,}\b", f"{title} {content[:500]}")
            matched = list(dict.fromkeys(caps))[:3] or ["General"]
        return matched[:5]

    return {
        "topic": match_tags(topic_keywords, "topic"),
        "category": match_tags(category_map, "category") or ["General"],
        "intent": match_tags(intent_keywords, "intent") or ["Reference"],
        "learning": match_tags(learning_keywords, "learning") or ["General"],
    }


async def generate_summary(title: str, content: str) -> dict:
    """Generate AI summaries using OpenAI or local fallback."""
    if not settings.has_openai:
        return _local_summarize(title, content)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.3,
        )

        prompt = f"""Analyze this saved content and return a JSON object with exactly these keys:
- short_summary: 2-3 sentence overview
- detailed_summary: 1-2 paragraph detailed summary
- key_insights: array of 3-5 key insights (strings)
- actionable_takeaways: array of 2-4 actionable takeaways (strings)

Title: {title}

Content:
{content[:8000]}

Return ONLY valid JSON, no markdown fences."""

        response = await llm.ainvoke([
            SystemMessage(content="You are an expert knowledge curator. Return only valid JSON."),
            HumanMessage(content=prompt),
        ])

        text = response.content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        result = json.loads(text)
        return {
            "short_summary": result.get("short_summary", ""),
            "detailed_summary": result.get("detailed_summary", ""),
            "key_insights": result.get("key_insights", []),
            "actionable_takeaways": result.get("actionable_takeaways", []),
        }
    except Exception:
        return _local_summarize(title, content)


async def generate_tags(title: str, content: str) -> dict:
    """Generate intelligent tags using OpenAI or local fallback."""
    if not settings.has_openai:
        return _local_tags(title, content)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )

        prompt = f"""Generate tags for this content. Return JSON with keys:
- topic: array of 3-5 topic tags (e.g. AI, Machine Learning)
- category: array of 1-3 category tags (e.g. Research, Tutorial, Career)
- intent: array of 1-2 intent tags (e.g. Learning, Reference, Implementation)
- learning: array of 1-2 learning level tags (e.g. Beginner, Advanced)

Title: {title}
Content excerpt: {content[:3000]}

Return ONLY valid JSON."""

        response = await llm.ainvoke([
            SystemMessage(content="You are a tagging expert. Return only valid JSON."),
            HumanMessage(content=prompt),
        ])

        text = response.content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        return json.loads(text)
    except Exception:
        return _local_tags(title, content)
