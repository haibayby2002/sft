import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))


from data.database import init_db, insert_deck, get_all_decks, insert_slide, get_slides_by_deck

init_db()

deck_id = insert_deck("Test Deck", "For testing only")
print("Created Deck ID:", deck_id)

slide_id = insert_slide(deck_id, "slide_hub/test_slide.pdf", "Test Slide")
print("Created Slide ID:", slide_id)

print("\nDecks:")
for deck in get_all_decks():
    print(dict(deck))

print("\nSlides in Deck:")
for slide in get_slides_by_deck(deck_id):
    print(dict(slide))
