# src/models/agents.py
from edsl import (
    Agent,
    Model,
    Scenario,
    QuestionFreeText,
    QuestionLinearScale,
)

# Default profiles if user doesn't provide any
DEFAULT_PROFILES = {
    "default_a": "28 year old product manager living in San Francisco. Enjoys jazz music, rock climbing on weekends, and trying new restaurants. Looking for someone who is adventurous and has a good sense of humor.",
    "default_b": "30 year old PhD student in literature. Avid reader, enjoys philosophical discussions, practicing yoga, and is a committed vegan. Values intellectual curiosity and authenticity in relationships.",
}

# Conversation guidelines
CONVERSATION_GUIDELINES = (
    "Speak casually, in first-person, as if you're meeting for the first time. "
    "Do **not** dump your full résumé; reveal details gradually and ask questions. "
    "Feel free to use humour or small-talk."
)


def create_agent(name, profile, default_profile):
    """Create an agent with the given name and profile."""
    return Agent(
        name=name,
        traits={
            "persona": profile or default_profile,
            "guidelines": CONVERSATION_GUIDELINES,
        },
    )


def get_opener(model_name, agent, service_name=None):
    """Get an opening message from an agent."""
    if service_name:
        model = Model(model_name, service_name=service_name)
        print(f"Model instance created for opener with service {service_name}: {model}")
    else:
        model = Model(model_name)
        print(f"Model instance created for opener: {model}")
    
    return (
        QuestionFreeText(
            question_name="opener",
            question_text=(
                "You are on a first date. Write a brief opening statement to introduce yourself and ask a question. "
                "DO NOT include your name at the beginning of your response as it will be added automatically. "
                "Just write your dialogue directly."
            ),
        )
        .by(model)
        .by(agent)
        .run()
        .select("opener")
        .first()
    )


def get_response(model_name, agent_self, agent_other, turn, speaker, history_txt, service_name=None):
    """Get a response from an agent based on conversation history."""
    if service_name:
        model = Model(model_name, service_name=service_name)
        print(f"Model instance created for response with service {service_name}: {model}")
    else:
        model = Model(model_name)
        print(f"Model instance created for response: {model}")
    
    scenario = Scenario(
        {
            "chat": history_txt.strip(),
            "persona": agent_self.traits["persona"],
            "partner_persona": agent_other.traits["persona"],
        }
    )

    q = QuestionFreeText(
        question_name=f"turn_{turn}_{speaker}",
        question_text=(
            "You are {{ persona }} on a first date with {{ partner_persona }}. \n\n"
            "{{ chat }}\n\n"
            "Respond in character (≤ 120 words). DO NOT include your name at the beginning of your response as "
            "it will be added automatically. Just write your dialogue directly."
        ),
    )

    return (
        q.by(model)
        .by(agent_self)
        .by(scenario)
        .run()
        .select(f"turn_{turn}_{speaker}")
        .first()
    )


def get_rating(model_name, agent, history_txt, service_name=None):
    """Get a rating from an agent based on conversation history."""
    if service_name:
        model = Model(model_name, service_name=service_name)
        print(f"Model instance created for rating with service {service_name}: {model}")
    else:
        model = Model(model_name)
        print(f"Model instance created for rating: {model}")
    
    rating_question = QuestionLinearScale(
        question_name="rating",
        question_text=(
            "{{ history }}\n\n"
            "On a scale of 1–10, how would you rate this date? "
            "(1 = Terrible • 10 = Amazing)\n"
            "IMPORTANT: Respond with just the number from 1-10. No words or explanations."
        ),
        question_options=list(range(1, 11)),  # 1-10 inclusive
        option_labels={1: "Terrible", 10: "Amazing"},
    )

    result = (
        rating_question.by(model)
        .by(agent)
        .by(Scenario({"history": history_txt}))
        .run()
        .select("rating")
        .first()
    )
    
    # Handle case where result might be None
    if result is None:
        return 5  # Default middle rating if no response
    
    # Try to convert to int, with fallback
    try:
        return int(result)
    except (ValueError, TypeError):
        # Try to extract a number if result is a string with text
        if isinstance(result, str):
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                return int(numbers[0])
        return 5  # Default to middle rating if conversion fails
