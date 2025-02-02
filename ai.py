import json
import base64
from openai import OpenAI
from globals import OPENAI_API_KEY
from pdf_processor import PDFProcessor


class EnglishAI:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def read_pdf_and_return_new_vocabulary(self, pdf_path: str) -> dict:
        """
        PDF faylni o'qib, undan ingliz tiliga oid so'zlarni topadi va ularning o'zbekcha tarjimasi bilan qaytaradi.

        Args:
            pdf_path (str): PDF fayl yo'li

        Returns:
            dict: Inglizcha so'zlar va ularning o'zbekcha tarjimasi
        """
        # PDF fayldan matnni olish
        pdf_processor = PDFProcessor(pdf_path)
        text = pdf_processor.extract_text_from_pages(1, pdf_processor.get_total_pages())

        # OpenAI ga so'rov yuborish
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant that analyzes English text and extracts ALL important vocabulary words. 
                    Your task is to:
                    1. Find ALL important and topic-relevant English words from the text
                    2. Include both individual words and important phrases
                    3. Focus on words that would be valuable for English learners
                    4. Provide accurate Uzbek translations
                    5. Return at least 20-30 words/phrases if the text is long enough
                    
                    Return the response as a JSON with English words/phrases as keys and their Uzbek translations as values.""",
                },
                {
                    "role": "user",
                    "content": f"Please analyze this text and extract ALL important English vocabulary words with their Uzbek translations. Don't skip any important words:\n\n{text}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        # Natijani JSON formatida qaytarish
        return json.loads(response.choices[0].message.content)

    def get_grammar_from_pdf(self, pdf_path: str) -> dict:
        """
        Pdf file ichidagi grammar ma'lumotlarini olish va ularni qaytarish.
        Bu function grammar titlelarini va asosiy mavzuning nomini qaytaradi.

        Args:
            pdf_path (str): PDF fayl yo'li

        Returns:
            dict: {
                'main_topic': {'number': int, 'title': str},
                'titles': list[str],
                'thread_id': str
            }
        """
        # PDF faylni rasmga o'tkazish
        pdf_processor = PDFProcessor(pdf_path)
        images = pdf_processor.convert_pdf_to_images()

        # OpenAI ga so'rov yuborish
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant that analyzes English learning materials and extracts grammar topics.
                Your task is to:
                1. Find the main topic number and title (e.g. "2 Home", "3 Family")
                2. Find ALL grammar topics/titles from the PDF
                3. Return them in a clear, organized format
                4. Include only grammar-related titles
                5. Keep the original English titles as they appear in the PDF
                6. Ignore non-grammar content
                
                Return the response as a JSON with:
                {
                    "main_topic": {
                        "number": 2,
                        "title": "Home"
                    },
                    "titles": ["Present Simple", "There is/are", ...]
                }""",
            }
        ]

        # Har bir rasmni message sifatida qo'shish
        for image in images:
            # Rasmni base64 formatiga o'tkazish
            image_base64 = base64.b64encode(image).decode("utf-8")

            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this page and extract the main topic and all grammar titles:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                }
            )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        # Natijani JSON formatida qaytarish
        result = json.loads(response.choices[0].message.content)
        result["thread_id"] = response.id

        return result

    def ai_create_grammar_lesson(self, grammar_info: dict) -> dict:
        """
        Men bergan grammar ma'lumotlarini asosida yangi grammar darsini yaratish.

        Args:
            grammar_info (dict): Grammar mavzu ma'lumotlari
                - title: Grammar mavzusi nomi
                - thread_id: Oldingi muloqot ID si

        Returns:
            dict: Notion page uchun formatda tayyorlangan dars ma'lumotlari
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert English teacher creating a comprehensive grammar lesson. 
                    Create the lesson with the following structure:
                    1. Title (h1)
                    2. Introduction (brief overview of the topic)
                    3. Main Rules (with clear examples)
                    4. Common Usage (real-life examples)
                    5. Practice Exercises (3-5 exercises)
                    6. Common Mistakes (what to avoid)
                    
                    Guidelines:
                    - Main explanations should be in English
                    - Use Uzbek for complex concepts and important notes
                    - Include plenty of examples
                    - Make it engaging and easy to understand
                    - Use emojis for better visual organization
                    
                    Return the response as a JSON object formatted for Notion API with these blocks:
                    {
                        "parent": {"page_id": "your-page-id"},
                        "properties": {
                            "title": [{"text": {"content": "Grammar Topic"}}]
                        },
                        "children": [
                            {
                                "object": "block",
                                "type": "heading_1",
                                "heading_1": {
                                    "rich_text": [{"text": {"content": "Title"}}]
                                }
                            },
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{"text": {"content": "Content..."}}]
                                }
                            }
                            // More blocks...
                        ]
                    }""",
                },
                {
                    "role": "user",
                    "content": f"Please create a comprehensive grammar lesson about: {grammar_info['title']}",
                },
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        # Natijani JSON formatida qaytarish
        result = json.loads(response.choices[0].message.content)
        result["thread_id"] = response.id

        return result


# if __name__ == "__main__":
#     # Test the class
#     ai = EnglishAI()

#     # Test grammar lesson creation
#     grammar_topic = {"title": "Grammar - Countable Nouns", "thread_id": "chat_abc123"}
#     lesson = ai.ai_create_grammar_lesson(grammar_topic)
#     print(json.dumps(lesson, indent=2, ensure_ascii=False))
