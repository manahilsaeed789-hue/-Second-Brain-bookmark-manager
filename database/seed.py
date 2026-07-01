"""Seed script — creates demo user and sample bookmarks."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.auth import create_user, hash_password
from backend.database import SessionLocal, init_db
from backend.models import User
from backend.services import bookmark_service

SAMPLE_CONTENT = [
    {
        "title": "Introduction to Neural Networks",
        "content": """Neural networks are computing systems inspired by biological neural networks. 
        They consist of layers of interconnected nodes (neurons) that process information. 
        Deep learning uses neural networks with many hidden layers to learn complex patterns 
        from data. Applications include image recognition, natural language processing, 
        and game playing. The backpropagation algorithm is used to train neural networks 
        by adjusting weights based on prediction errors. Popular architectures include 
        CNNs for images, RNNs for sequences, and Transformers for language tasks.""",
        "source_type": "paste",
    },
    {
        "title": "10 Productivity Tips for Developers",
        "content": """1. Use the Pomodoro Technique - work in 25-minute focused sessions.
        2. Keep a clean development environment with minimal distractions.
        3. Automate repetitive tasks with scripts and tools.
        4. Practice time blocking for deep work sessions.
        5. Use version control religiously for all projects.
        6. Take regular breaks to maintain focus and creativity.
        7. Learn keyboard shortcuts for your IDE and tools.
        8. Document your code and decisions as you go.
        9. Set clear daily goals the night before.
        10. Review and reflect on your workflow weekly.""",
        "source_type": "note",
    },
    {
        "title": "Understanding Transformer Architecture",
        "content": """The Transformer architecture, introduced in 'Attention Is All You Need' (2017), 
        revolutionized natural language processing. Key components include self-attention mechanisms 
        that allow the model to weigh the importance of different words in a sequence. Multi-head 
        attention enables the model to focus on different representation subspaces. Position encoding 
        provides sequence order information. The encoder-decoder structure processes input and 
        generates output sequences. Transformers power modern LLMs like GPT, BERT, and Claude. 
        They scale efficiently with compute and data, making them the foundation of current AI systems.""",
        "source_type": "paste",
    },
    {
        "title": "Career Guide: Breaking into Tech",
        "content": """Breaking into the tech industry requires a strategic approach. Build a portfolio 
        of projects that demonstrate your skills. Contribute to open source to gain experience and 
        visibility. Network actively through meetups, conferences, and online communities. 
        Prepare thoroughly for technical interviews focusing on data structures, algorithms, 
        and system design. Consider bootcamps or self-study paths based on your learning style. 
        Tailor your resume to highlight relevant projects and skills. Practice behavioral 
        interview questions using the STAR method. Don't underestimate the power of referrals 
        in getting your foot in the door.""",
        "source_type": "note",
    },
    {
        "title": "Focus and Deep Work Strategies",
        "content": """Deep work, as defined by Cal Newport, is professional activity performed in a 
        state of distraction-free concentration that pushes cognitive capabilities to their limit. 
        Strategies for achieving deep work include: scheduling dedicated deep work blocks, 
        eliminating digital distractions, creating rituals to enter deep work mode, embracing boredom 
        to strengthen focus muscles, and quitting social media during work hours. The ability to 
        perform deep work is becoming increasingly rare and valuable in our economy. Research shows 
        that context switching can reduce productivity by up to 40%. Building a deep work practice 
        requires intentional effort but pays dividends in output quality and career advancement.""",
        "source_type": "paste",
    },
]


async def seed():
    init_db()
    db = SessionLocal()

    try:
        # Create demo user if not exists
        demo = db.query(User).filter(User.email == "demo@secondbrain.app").first()
        if not demo:
            demo = create_user(db, "demo@secondbrain.app", "demo", "demo1234")
            print(f"Created demo user: demo@secondbrain.app / demo1234")
        else:
            print("Demo user already exists, skipping user creation")

        # Check if bookmarks already exist
        from backend.models import Bookmark
        existing = db.query(Bookmark).filter(Bookmark.user_id == demo.id).count()
        if existing > 0:
            print(f"User already has {existing} bookmarks, skipping seed data")
            return

        print("Creating sample bookmarks (this may take a moment for embeddings)...")
        for item in SAMPLE_CONTENT:
            await bookmark_service.create_bookmark_from_content(
                db, demo.id, item["title"], item["content"], item["source_type"]
            )
            print(f"  [OK] {item['title']}")

        print(f"\nSeed complete! Login with demo@secondbrain.app / demo1234")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed())
