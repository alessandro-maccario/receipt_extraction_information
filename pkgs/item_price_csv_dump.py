"""
This script takes a list of tuples (item, price), tokenize the words and cross check them with the German
dictionary. It returns again a list of tuples (item, price) with the corrected words.

Reference
- https://github.com/wolfgarbe/SymSpell
"""

from symspellpy import SymSpell, Verbosity

###################################
# Spacy and Syspell for tokenization and spelling correction
# download small model
# !python -m spacy download de_core_news_sm

# # Load the Small German dictionary taken from Leipzig Corpora
# nlp_sm = spacy.load("de_core_news_sm")


def item_price_preprocess(nlp, text_item_price) -> list[tuple]:
    # instantiate SymSpell obkect
    sym_spell = SymSpell(max_dictionary_edit_distance=2)
    # load SymSpell German dictionary
    sym_spell.load_dictionary(
        "data/de_polished.txt", term_index=0, count_index=1, encoding="utf-8"
    )

    # # test if the algorithm works
    # text_item_price = [
    #     ("X Glas Masser Ieer", "0.00"),
    #     ("Salat groß", "2.40"),
    #     (" Metto", "2.10"),
    #     ("Sumne", "2.40"),
    # ]
    # print("\n")

    # create a list to store the fixed (item, price) tuple
    fixed_item_price_list = []

    for text_item_tup in text_item_price:
        # create a list to store the corrected item and price
        text_item_price_corrected = []
        # grab only the text of the tuple
        clean_text = text_item_tup[0].strip()
        # grab only the price of the tuple
        item_price = text_item_tup[1]

        # process the all text of the tuple
        doc = nlp(clean_text)
        print("\nToken:", doc)

        # Tokenization
        # print("Tokens:", [token.text for token in doc])

        for token in doc:
            # Test word
            input_word = token.text
            suggestions = sym_spell.lookup(
                input_word, Verbosity.TOP, max_edit_distance=2
            )

            # Print suggestions
            if suggestions:
                for suggestion in suggestions:
                    # print("Correct Token:", suggestion.term)
                    # new_token_list.append(suggestion.term)

                    # substitute the text with the new correct string
                    text = "".join(suggestion.term)
                    # print("\nCorrected text:", text)

                    # append to list and join each string word
                    text_item_price_corrected.append(text)
                    text_item_price_corrected_joined = " ".join(
                        text_item_price_corrected
                    )

                    break
                    # print(f"Suggestion: {suggestion.term}, Distance: {suggestion.distance}, Frequency: {suggestion.count}")
            else:
                print("No suggestions found.")
                text_item_price_corrected_joined = ""

        # save the corrected text and the price in a tuple
        fixed_item_price_list.append((text_item_price_corrected_joined, item_price))

    # print(text_item_price_corrected_joined)
    print(fixed_item_price_list)

    return fixed_item_price_list
