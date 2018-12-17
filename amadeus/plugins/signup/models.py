from amadeus.db import make_table_name, db


class Event(db.Model):
    __tablename__ = make_table_name('signup', 'events')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(100), nullable=False)
    fields = db.Column(db.JSON, nullable=False)
    context_id = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer)
    qq_group_number = db.Column(db.BigInteger)

    def __repr__(self):
        return f'<Event (id={self.id}, title={self.title})>'


class Signup(db.Model):
    __tablename__ = make_table_name('signup', 'signups')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    context_id = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer,
                         db.ForeignKey(f'{Event.__tablename__}.id'),
                         nullable=False)
    field_values = db.Column(db.JSON, nullable=False)
    qq_number = db.Column(db.BigInteger)

    @db.declared_attr
    def __table_args__(cls):
        return db.UniqueConstraint('context_id', 'event_id')
