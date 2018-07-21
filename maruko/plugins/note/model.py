from sqlalchemy import Column, Integer, Text

from maruko.db import make_table_name, Base


class Note(Base):
    __tablename__ = make_table_name('note', 'notes')

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)

    def __repr__(self):
        return f'<Note (id={self.id}, content={repr(self.content[:10])})>'
