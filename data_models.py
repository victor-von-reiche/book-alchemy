from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return (f"Author(self.id={self.id}, name={self.name}, birth_date={self.birth_date}, "
                f"date_of_death={self.date_of_death})")

    def __str__(self):
        return f"Author(self.id={self.id}, name={self.name})"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    author = db.relationship("Author", backref="books")

    def __repr__(self):
        return (f"Book(book_id={self.id}, isbn={self.isbn}, title={self.title}, "
                f"publish_year={self.publication_year}), author_id={self.author_id})")

    def __str__(self):
        return f"Book(id={self.id}, title={self.title})"
