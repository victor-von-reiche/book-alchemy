from flask import Flask, render_template, redirect, url_for
from datetime import datetime
from pygments.lexers import templates
from data_models import db, Author, Book
import os
from flask import request
from flask import flash
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_key")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)
db.init_app(app)

"""with app.app_context():
    db.create_all()"""


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Add a new author to the database"""
    if request.method == "POST":

        # Converting String → date
        birth_date_str = request.form.get("birth_date")
        birth_date = (
            datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            if birth_date_str
            else None
        )

        date_of_death_str = request.form.get("date_of_death")
        date_of_death = (
            datetime.strptime(date_of_death_str, "%Y-%m-%d").date()
            if date_of_death_str
            else None
        )

        name = request.form["name"]
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        db.session.add(author)
        db.session.commit()
        return render_template("add_author.html", message="Author added successfully!")
    else:
        return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Add a new book to the database"""
    if request.method == "POST":
        isbn = request.form["isbn"]
        title = request.form["title"]
        publication_year = request.form["publication_year"]
        author_id = request.form["author_id"]

        db.session.add(
            Book(
                isbn=isbn,
                title=title,
                publication_year=publication_year,
                author_id=author_id,
            )
        )
        db.session.commit()
        return render_template("add_book.html", message="Book added successfully!")
    else:
        authors = Author.query.all()
        return render_template("add_book.html", authors=authors)


@app.route("/")
def main_page():

    # default for sorting = title
    sort = request.args.get("sort", "title")

    if sort == "title":
        books = Book.query.order_by(Book.title).all()
    elif sort == "author":
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.all()

    search = request.args.get("search")
    if search:
        books = Book.query.filter(Book.title.ilike(f"%{search}%")).all()

    return render_template("home.html", books=books)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    if not book.author.books:
        db.session.delete(book.author)
        flash("Book deleted successfully!", "success")
    db.session.commit()

    return redirect(url_for("main_page"))


if __name__ == "__main__":
    app.run(debug=True)
