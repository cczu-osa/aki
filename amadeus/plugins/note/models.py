from amadeus.db import make_table_name, db


class Note(db.Model):
    __tablename__ = make_table_name('note', 'notes')

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    content = db.Column(db.Text(), nullable=False)
    context_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Note (id={self.id}, content={repr(self.content[:10])})>'
