from datetime import datetime
from typing import Optional
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field, Column, Relationship, DateTime, Enum, JSON


class TimestampMixin(object):
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)


#
# 単語帳関連データ
#

class WordType(SQLModel, table=True):
    __tablename__ = "word_types"

    id: int = Field(default=None, primary_key=True)
    title_en: str
    title_jp: str
    title_short_en: str
    title_short_jp: str


class WordBook(SQLModel, TimestampMixin, table=True):
    __tablename__ = "word_books"

    id: int = Field(default=None, primary_key=True)
    title: str
    short_name: str | None
    author: str | None
    publisher: str | None
    year: int | None
    version: int | None
    isbn: str | None
    note: str | None

    word_items: list["WordItem"] = Relationship(back_populates="word_book")
    vocab_quizzes: list["VocabQuiz"] = Relationship(back_populates="word_book")


class WordItem(SQLModel, TimestampMixin, table=True):
    __tablename__ = "word_items"

    id: int = Field(default=None, primary_key=True)
    word_book_id: int = Field(foreign_key="word_books.id")
    is_active: bool = Field(default=True)
    seq_no: int
    word: str
    section_no: str | None
    section_title: str | None
    pronunciation: str | None
    pronunciation_kana: str | None

    word_book: WordBook = Relationship(back_populates="word_items")
    word_meanings: list["WordMeaning"] = Relationship(back_populates="word_item")
    word_sentences: list["WordSentence"] = Relationship(back_populates="word_item")


class WordMeaning(SQLModel, TimestampMixin, table=True):
    __tablename__ = "word_meanings"

    id: int = Field(default=None, primary_key=True)
    word_item_id: int = Field(foreign_key="word_items.id")
    seq_no: int
    word_type: int = Field(foreign_key="word_types.id")
    sub_word_type: int | None = Field(foreign_key="word_types.id")
    meaning: str
    note: str | None

    word_item: WordItem = Relationship(back_populates="word_meanings")


class WordSentence(SQLModel, TimestampMixin, table=True):
    __tablename__ = "word_sentences"

    id: int = Field(default=None, primary_key=True)
    word_item_id: int = Field(foreign_key="word_items.id")
    seq_no: int
    sentence: str
    note: str | None

    word_item: WordItem = Relationship(back_populates="word_sentences")


class VocabQuiz(SQLModel, TimestampMixin, table=True):
    __tablename__ = "vocab_quizzes"

    id: int = Field(default=None, primary_key=True)
    word_book_id: int = Field(foreign_key="word_books.id")
    uuid: str
    title: str
    description: str | None
    author: str | None
    quiz_dt: datetime | None
    quiz_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    word_book: WordBook = Relationship(back_populates="vocab_quizzes")


class WordItemInfo(SQLModel, table=False):
    word_item_id: int
    seq_no: int
    word: str
    meaning: str


class VocabQuizInputParam(SQLModel, table=False):
    title: str
    description: str | None
    area: Optional[list]
    quiz_dt: datetime | None
    count: int | None

