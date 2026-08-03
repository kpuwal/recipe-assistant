def detect_intent(message: str) -> str:

    msg = message.lower().strip()

    #
    # KNOWLEDGE
    #
    if msg.startswith((
        "hoe ",
        "waarom ",
        "wanneer ",
        "wat is ",
        "wat zijn ",
        "welke ",
        "hoeveel "
    )):
        return "knowledge"

    #
    # SUBSTITUTION
    #
    substitution_words = [
        "vervang",
        "vervangen",
        "alternatief",
        "substituut",
        "in plaats van"
    ]

    if any(word in msg for word in substitution_words):
        return "substitution"

    #
    # AI RECIPE / MEAL IDEAS
    #
    meal_words = [
        "ik heb",
        "wat kan ik maken",
        "restjes",
        "maak iets met",
        "bedenk recept",
        "genereer recept",
        "nieuw recept"
    ]

    if any(word in msg for word in meal_words):
        return "ai_recipe"

    return "search"
