from sqlalchemy import Column, Integer, Text
from flask_sqlalchemy import SQLAlchemy

# cf. http://flask.pocoo.org/docs/0.12/patterns/appfactories/
db = SQLAlchemy()


class Doc(db.Model):
    __tablename__ = "docs"
    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)
    doc = Column(Text, nullable=False)

    def __repr__(self):
        if len(self.doc) > 20:
            short_doc = self.doc[:20] + "..."
        else:
            short_doc = self.doc
        return "<Doc(id=%d, url='%s' doc='%s'>" % (
            self.id, self.url, short_doc)
