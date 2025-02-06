from pick import pick
import asyncio
from notion import NotionManager

notion_manager = NotionManager()

async def select_vocabulary_page():
    """
    User can select a page to save vocabulary words
    
    Returns:
        str: Selected page ID
    """
    # Get all pages
    pages = await notion_manager.get_all_pages()
    
    # Prepare options for selection
    options = []
    for page in pages:
        try:
            if "title" in page["properties"]:
                title = page["properties"]["title"]["title"][0]["text"]["content"]
                options.append((title, page["id"]))
        except (KeyError, IndexError):
            continue
    
    # If no pages found
    if not options:
        raise Exception("No pages found in your Notion workspace")
    
    # Show selection menu
    title = "Select a page to save vocabulary words (use ↑↓ arrows and press ENTER):"
    option, index = pick([x[0] for x in options], title)
    
    # Return selected page ID
    return options[index][1]

async def select_lesson_page():
    """
    User can select a page to create new lesson
    
    Returns:
        str: Selected page ID
    """
    # Get all lesson pages
    pages = await notion_manager.get_all_lesson_pages()
    
    # Prepare options for selection
    options = [(page["title"], page["id"]) for page in pages]
    
    # If no pages found
    if not options:
        raise Exception("No lesson pages found")
    
    # Show selection menu
    title = "Select a page to create new lesson (use ↑↓ arrows and press ENTER):"
    option, index = pick([x[0] for x in options], title)
    
    # Return selected page ID
    return options[index][1]

# Example usage
async def main():
    try:
        vocabulary_page_id = await select_vocabulary_page()
        print(f"Selected vocabulary page ID: {vocabulary_page_id}")
        
        lesson_page_id = await select_lesson_page()
        print(f"Selected lesson page ID: {lesson_page_id}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
