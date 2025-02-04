from notion_client import AsyncClient
from globals import NOTION_TOKEN
import asyncio
from database import create_word, word_exists


class NotionManager:
    def __init__(self):
        self.client = AsyncClient(auth=NOTION_TOKEN)

    async def add_vocabulary(self, word: str, translation: str):
        """
        Add new word to vocabulary database with capitalized first letters
        """
        word = word.strip().capitalize()
        translation = translation.strip().capitalize()

        await self.client.pages.create(
            parent={"database_id": "18eb8b92-d213-80ee-ae0f-d8a4d0ba4c69"},
            properties={
                "Enlish": {"title": [{"text": {"content": word}}]},
                "O'zbek": {"rich_text": [{"text": {"content": translation}}]},
            },
        )

    async def create_grammar_page(self, title: str):
        """
        Create new grammar topic page. Return page id
        """
        new_page = await self.client.pages.create(
            parent={"page_id": ""},
            properties={"title": {"title": [{"text": {"content": title}}]}},
        )

        return new_page["id"]

    async def check_word_exists(self, word: str) -> bool:
        """
        Check if word already exists in vocabulary database
        """
        response = await self.client.databases.query(
            database_id="18eb8b92-d213-80ee-ae0f-d8a4d0ba4c69",
            filter={"property": "Word", "title": {"equals": word}},
        )
        return len(response["results"]) > 0

    async def get_all_pages(self):
        """
        Get all pages from vocabulary database
        """
        response = await self.client.search(
            query="",
        )
        return response["results"]

    async def get_dictionary_database(self):
        """
        Get dictionary database
        """
        response = await self.client.databases.query(
            database_id="18eb8b92-d213-80ee-ae0f-d8a4d0ba4c69",
        )
        return response["results"][0]

    async def get_all_words_and_update_database(self):
        """
        Get all words from vocabulary database and update database with capitalized first letters
        """
        response = await self.client.databases.query(
            database_id="18eb8b92-d213-80ee-ae0f-d8a4d0ba4c69",
        )

        saved_words = 0
        skipped_words = 0

        for page in response["results"]:
            try:
                # Extract English and Uzbek words from Notion page
                english_word = (
                    page["properties"]["Enlish"]["title"][0]["text"]["content"]
                    .strip()
                    .capitalize()
                )
                uzbek_word = (
                    page["properties"]["O'zbek"]["rich_text"][0]["text"]["content"]
                    .strip()
                    .capitalize()
                )

                # Check if word already exists in database
                if not word_exists(english_word):
                    # Create new word in database
                    word = create_word(english=english_word, uzbek=uzbek_word)
                    if word:
                        saved_words += 1
                else:
                    skipped_words += 1

            except (KeyError, IndexError) as e:
                print(f"Error processing page: {e}")
                continue

        return {
            "saved_words": saved_words,
            "skipped_words": skipped_words,
            "total_processed": saved_words + skipped_words,
        }

    async def get_all_lesson_pages(self):
        """
        Get all lesson pages with their titles and IDs
        """
        response = await self.client.blocks.children.list(
            block_id="18eb8b92-d213-8024-ab92-ee904d792d47"
        )

        lesson_pages = []
        for block in response["results"]:
            if block["type"] == "child_page":
                lesson_pages.append(
                    {"id": block["id"], "title": block["child_page"]["title"]}
                )

        return lesson_pages

    async def create_lesson_page(self, title: str):
        """
        Create a new lesson page
        """
        new_page = await self.client.pages.create(
            parent={"page_id": "18eb8b92-d213-8024-ab92-ee904d792d47"},
            properties={"title": {"title": [{"text": {"content": title}}]}},
        )
        return new_page["id"]

    async def create_grammar_page(self, page_id: str, children: list):
        """
        Create a new grammar page with content
        """
        response = await self.client.blocks.children.append(
            block_id=page_id,
            children=children,
        )
        return response

    async def update_children_in_the_page(self, page_id: str, children: list):
        """
        Update children in the page
        """
        response = await self.client.blocks.children.update(
            block_id=page_id,
            children=children,
        )
        return response


# async def main():
#     notion_manager = NotionManager()

#     # Sync words from Notion to local database
#     result = await notion_manager.get_all_words_and_update_database()
#     print(f"Sync results:")
#     print(f"- Saved new words: {result['saved_words']}")
#     print(f"- Skipped existing words: {result['skipped_words']}")
#     print(f"- Total processed: {result['total_processed']}")


# add new word to vocabulary database
# async def main():
#     notion_manager = NotionManager()
#     await notion_manager.add_vocabulary("phone", "telefon")


# add new lesson and save grammars
# async def main():
#     notion_manager = NotionManager()
#     pages = await notion_manager.get_all_lesson_pages()
#     print("\nLesson Pages:")
#     for page in pages:
#         print(f"Title: {page['title']}")
#         print(f"ID: {page['id']}")
#         print("-" * 30)


# create new lesson page
async def main():
    notion_manager = NotionManager()
    # page_id = await notion_manager.create_lesson_page("Lesson 2")
    await notion_manager.update_children_in_the_page(
        "190b8b92-d213-81a2-b724-c5eb2b0f5396",
        [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": "There is – There are"}}]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "In this lesson, we will explore the use of 'There is' and 'There are' in English grammar. These phrases are essential for indicating the existence or presence of something. Understanding how to use them correctly will help you describe objects and situations effectively."
                            }
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": "Main Rules"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "1. 'There is' is used for singular nouns and uncountable nouns. \n   - Example: There is a cat in the garden. \n   - Example: There is milk in the fridge."
                            }
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "2. 'There are' is used for plural nouns.\n   - Example: There are five books on the table.\n   - Example: There are many stars in the sky."
                            }
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": "Common Usage"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "In real-life conversations, 'There is' and 'There are' help you describe environments and situations. For example:\n\n- \"There is a meeting at 10 AM.\"\n- \"There are two options to choose from.\"\n\n⚠️ Note: In spoken English, 'There's' is a common contraction for 'There is'."
                            }
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": "Practice Exercises"}}]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "1. Fill in the blanks with 'There is' or 'There are':\n   - _______ a dog outside.\n   - _______ three apples on the counter.\n\n2. Rewrite the sentences using 'There is' or 'There are':\n   - A book is on the desk.\n   - Many people are in the park.\n\n3. Correct the mistakes in the following sentences:\n   - There is two cats in the garden.\n   - There are a cake on the table."
                            }
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": "Common Mistakes"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "🚫 Avoid these common mistakes:\n\n1. Using 'There is' with plural nouns.\n   - Incorrect: There is many cars in the parking lot.\n   - Correct: There are many cars in the parking lot.\n\n2. Using 'There are' with uncountable nouns.\n   - Incorrect: There are milk in the fridge.\n   - Correct: There is milk in the fridge.\n\n📌 Important: Remember, 'There is' is for singular and uncountable nouns, while 'There are' is for plural nouns (Uzbek: 'There is' birlik va sanalmas nomlar uchun ishlatiladi, 'There are' ko'plik nomlar uchun.)"
                            }
                        }
                    ]
                },
            },
        ],
    )


# Example testing
if __name__ == "__main__":
    asyncio.run(main())
