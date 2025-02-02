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
    page_id = await notion_manager.create_lesson_page("Lesson 2")
    await notion_manager.create_grammar_page(
        page_id,
        [
            {
                "paragraph": {
                    "text": [{"text": {"content": "This is a test grammar page"}}]
                }
            }
        ],
    )


# Example testing
# if __name__ == "__main__":
#     asyncio.run(main())
