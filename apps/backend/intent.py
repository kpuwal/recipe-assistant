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

# def detect_intent(message: str):

#     msg = message.lower()

#     recipe_words = [
#         "onder",
#         "boven",
#         "tussen",
#         "recept",
#         "recepten",
#         "kip",
#         "pasta",
#         "rijst",
#     ]

#     if any(word in msg for word in recipe_words):
#         return "search"

#     if any(
#         phrase in msg
#         for phrase in [
#             "vervang",
#             "alternatief",
#             "substituut",
#             "kan ik vervangen"
#         ]
#     ):
#         return "substitution"

#     if any(
#         phrase in msg
#         for phrase in [
#             "ik heb",
#             "restjes",
#             "wat kan ik maken"
#         ]
#     ):
#         return "meal_idea"

#     if any(
#         msg.startswith(word)
#         for word in [
#             "hoe",
#             "waarom",
#             "wanneer",
#             "wat is"
#         ]
#     ):
#         return "knowledge"

#     return "search"