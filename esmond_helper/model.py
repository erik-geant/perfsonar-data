from sqlalchemy import Column, Integer, Text
from flask_sqlalchemy import SQLAlchemy

# cf. http://flask.pocoo.org/docs/0.12/patterns/appfactories/
db = SQLAlchemy()


class Doc(db.Model):
    __tablename__ = "docs"
    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)
    # sqlite doesn't have datetime types
    expires = Column(Integer, nullable=True)
    doc = Column(Text, nullable=False)

    def __repr__(self):
        if len(self.doc) > 20:
            short_doc = self.doc[:20] + "..."
        else:
            short_doc = self.doc
        return "<Doc(id=%d, url='%s', expires='%d', doc='%s'>" % (
            self.id, self.url, self.expires, short_doc)
