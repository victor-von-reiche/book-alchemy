from flask import Flask, render_template, redirect, url_for
from datetime import datetime
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
    """Handle adding a new author via form submission (GET shows form, POST saves to DB)."""
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
    """Handle adding a new book via form submission (GET shows form with authors, POST saves to DB)."""
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
    """Render the homepage with a list of books, supporting optional search and sorting."""

    # default for sorting = title
    sort = request.args.get("sort", "title")
    search = request.args.get("search")
    query = Book.query

    if search:
        query = query.filter(Book.title.ilike(f"%{search}%"))

    if sort == "title":
        query = query.order_by(Book.title)
    elif sort == "author":
        query = query.join(Author).order_by(Author.name)

    books = query.all()

    return render_template("home.html", books=books)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a book by ID; also remove the author if they have no other books."""

    book = db.session.get(Book, book_id)
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("main_page"))

    author = book.author
    try:
        db.session.delete(book)
        if not author.books:
            db.session.delete(author)
        db.session.commit()
        flash("Book deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting book: {str(e)}", "error")

    return redirect(url_for("main_page"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
