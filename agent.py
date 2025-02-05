import asyncio
from pdf_processor import PDFProcessor
from ai import EnglishAI
from notion import NotionManager
from database import word_exists

english_ai = EnglishAI()
notion_manager = NotionManager()


async def start_agent(message: str):
    """Start the agent with a lesson request"""
    try:
        start_page, end_page = message.split("-")
        print(f"🔍 Start page: {start_page}, End page: {end_page}")

        pdf_processor = PDFProcessor("A1.pdf")
        new_pdf_path = pdf_processor.extract_pages(int(start_page), int(end_page))
        print(f"🔍 New PDF path: {new_pdf_path}")

        vocabulary = english_ai.read_pdf_and_return_new_vocabulary(new_pdf_path)
        print(f"🔍 Vocabulary count: {len(vocabulary)}")

        await notion_manager.get_all_words_and_update_database()
        # yangi so'zni databasedan tekshirish kerak u yerda bo'lmasa uni notionga qo'shish kerak
        new_words = [word for word in vocabulary if not word_exists(word.capitalize())]

        for word in new_words:
            await notion_manager.add_vocabulary(word, vocabulary[word])
        print("✅ Vocabulary added successfully")

        grammar_titles = english_ai.get_grammar_from_pdf(new_pdf_path)
        print(f"🔍 Grammar main topic: {grammar_titles['main_topic']}")
        print(f"👨‍💻 Get new grammar titles count: {len(grammar_titles['titles'])}")

        lesson_page_id = await notion_manager.create_lesson_page(
            f"{grammar_titles['main_topic']['number']}-dars. {grammar_titles['main_topic']['title']}"
        )
        print(f"🔍 Created new notion page:: {lesson_page_id}")

        # hozirchalik titlelardan faqat 2 tasini yuborish kerak
        # titles = grammar_titles["titles"][:2]
        titles = grammar_titles["titles"]

        content = []
        for title in titles:
            print(f"⚡️ Creating grammar lesson for: {title}")
            response = english_ai.ai_create_grammar_lesson(title)
            content.extend(response["children"])
            # yangi titledan oldin divider qo'shish kerak
            content.append({"object": "block", "type": "divider", "divider": {}})

        print(f"🔍 Content: {content}")
        await notion_manager.update_children_in_the_page(lesson_page_id, content)

        print("✅ Grammar lesson created successfully")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main():
    input_message = input("Enter the page range: ")
    await start_agent(input_message)


if __name__ == "__main__":
    asyncio.run(main())
