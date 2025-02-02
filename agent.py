from telegram import Bot
from globals import TELEGRAM_TOKEN, OPENAI_API_KEY
from pdf_processor import PDFProcessor
from notion import NotionManager
from openai import AsyncOpenAI
import json

class EnglishNoteAgent:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.notion = NotionManager()
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.pdf_processor = None

    async def process_lesson(self, pdf_path: str, lesson_number: int, page_range: tuple, chat_id: str):
        """Process a lesson and create notes"""
        try:
            await self.send_message_to_user(f"Starting to process lesson {lesson_number}...", chat_id)
            
            # Initialize PDF processor
            self.pdf_processor = PDFProcessor(pdf_path)
            
            # Extract text from specified pages
            text = self.pdf_processor.extract_text_from_pages(page_range[0], page_range[1])
            
            # Analyze text with OpenAI
            await self.analyze_and_create_notes(text, lesson_number, chat_id)
            
            await self.send_message_to_user("✅ Lesson processing completed!", chat_id)
            
        except Exception as e:
            await self.send_message_to_user(f"❌ Error processing lesson: {str(e)}", chat_id)

    async def analyze_and_create_notes(self, text: str, lesson_number: int, chat_id: str):
        """Analyze text and create notes in Notion"""
        # Analyze vocabulary
        await self.send_message_to_user("Analyzing vocabulary...", chat_id)
        vocabulary_response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "Extract new English words and their translations from the text. Return as JSON array with format: [{word: string, translation: string}]"
            }, {
                "role": "user",
                "content": text
            }]
        )
        
        vocabulary = json.loads(vocabulary_response.choices[0].message.content)
        
        # Add vocabulary to Notion
        new_words = []
        for item in vocabulary:
            if not await self.notion.check_word_exists(item["word"]):
                await self.notion.add_vocabulary(item["word"], item["translation"])
                new_words.append(f"{item['word']} - {item['translation']}")
        
        if new_words:
            await self.send_message_to_user("📚 New vocabulary added:\n" + "\n".join(new_words), chat_id)
        
        # Analyze grammar
        await self.send_message_to_user("Analyzing grammar topics...", chat_id)
        grammar_response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "Analyze the text and identify grammar topics. For each topic, provide a detailed explanation with rules and examples. Return as JSON array with format: [{topic: string, explanation: string}]"
            }, {
                "role": "user",
                "content": text
            }]
        )
        
        grammar_topics = json.loads(grammar_response.choices[0].message.content)
        
        # Create grammar pages in Notion
        for topic in grammar_topics:
            page_id = await self.notion.create_grammar_page(
                f"Lesson {lesson_number} - {topic['topic']}", 
                topic['explanation']
            )
            await self.send_message_to_user(f"📝 Created grammar note: {topic['topic']}", chat_id)

    async def send_message_to_user(self, message: str, chat_id: str):
        """Send message to user via Telegram"""
        await self.bot.send_message(chat_id=chat_id, text=message)

async def start_agent(message: str, chat_id: str):
    """Start the agent with a lesson request"""
    try:
        # Parse message format: "Lesson 3: 100-120"
        parts = message.split(":")
        lesson_info = parts[0].strip()
        pages = parts[1].strip().split("-")
        
        lesson_number = int(lesson_info.split()[1])
        page_range = (int(pages[0]), int(pages[1]))
        
        agent = EnglishNoteAgent()
        await agent.process_lesson("path_to_your_pdf.pdf", lesson_number, page_range, chat_id)
        
    except Exception as e:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=chat_id, 
            text=f"❌ Error: {str(e)}\nPlease use format: 'Lesson X: START_PAGE-END_PAGE'"
        )
