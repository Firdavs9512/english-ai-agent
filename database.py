from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from typing import Optional, Union

# Create database engine
engine = create_engine('sqlite:///vocabulary.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Word(Base):
    __tablename__ = 'vocabulary'
    
    id = Column(Integer, primary_key=True)
    english = Column(String, unique=True, nullable=False)
    uzbek = Column(String, nullable=False)
    is_memorized = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Word(english='{self.english}', uzbek='{self.uzbek}', is_memorized={self.is_memorized})>"

def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(engine)

def word_exists(word: str, language: str = 'english') -> bool:
    """
    Check if word exists in database
    
    Args:
        word (str): Word to check
        language (str): Language of the word ('english' or 'uzbek')
    
    Returns:
        bool: True if word exists, False otherwise
    """
    word = word.strip().capitalize()
    session = Session()
    try:
        if language == 'english':
            exists = session.query(Word).filter(Word.english == word).first() is not None
        else:
            exists = session.query(Word).filter(Word.uzbek == word).first() is not None
        return exists
    finally:
        session.close()

def create_word(english: str, uzbek: str) -> Union[Word, None]:
    """
    Create new word in database with capitalized first letters
    
    Args:
        english (str): English word
        uzbek (str): Uzbek translation
    
    Returns:
        Word: Created word object or None if creation failed
    """
    english = english.strip().capitalize()
    uzbek = uzbek.strip().capitalize()
    
    session = Session()
    try:
        word = Word(english=english, uzbek=uzbek)
        session.add(word)
        session.commit()
        return word
    except IntegrityError:
        session.rollback()
        return None
    finally:
        session.close()

def get_word(text: str, language: str = 'english') -> Optional[Word]:
    """
    Get word by text in specified language
    
    Args:
        text (str): Word to search
        language (str): Language of the word ('english' or 'uzbek')
    
    Returns:
        Optional[Word]: Word object if found, None otherwise
    """
    text = text.strip().capitalize()
    session = Session()
    try:
        if language == 'english':
            word = session.query(Word).filter(Word.english == text).first()
        else:
            word = session.query(Word).filter(Word.uzbek == text).first()
        return word
    finally:
        session.close()

# Initialize database when module is imported
init_db()
