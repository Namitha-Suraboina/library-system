from flask import Flask, request, jsonify
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_DATABASE_PASSWORD'] = '45298'  # Replace with your MySQL password
app.config['MYSQL_DATABASE_DB'] = 'library'  # Replace with your MySQL database name
app.config['MYSQL_DATABASE_HOST'] = 'localhost'  # Replace with your MySQL host
mysql = MySQL(app)

class Book:
    def __init__(self, ISBN, title, author):
        self.ISBN = ISBN
        self.title = title
        self.author = author

    def to_dict(self):
        return {
            'ISBN': self.ISBN,
            'title': self.title,
            'author': self.author,
        }

class Library:
    @staticmethod
    def add_book(book):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (ISBN, title, author) VALUES (%s, %s, %s)",
                       (book.ISBN, book.title, book.author))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_books():
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ISBN, title, author FROM books")
        books = [Book(*row) for row in cursor.fetchall()]
        conn.close()
        return [book.to_dict() for book in books]

    @staticmethod
    def search_by_isbn(ISBN):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ISBN, title, author FROM books WHERE ISBN = %s", (ISBN))
        row = cursor.fetchone()
        conn.close()
        return Book(*row).to_dict() if row else None

    @staticmethod
    def delete_by_isbn(ISBN):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE ISBN = %s", (ISBN))
        conn.commit()
        conn.close()


@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        ISBN = data.get('ISBN')
        title = data.get('title')
        author = data.get('author')

        if not ISBN or not title or not author:
            raise ValueError("ISBN, title, and author are required fields")

        new_book = Book(ISBN=ISBN, title=title, author=author)
        Library.add_book(new_book)
        return jsonify({'message': 'Book added successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/list_books', methods=['GET'])
def list_books():
    all_books = Library.get_all_books()
    return jsonify(all_books)

@app.route('/search_book/<ISBN>', methods=['GET'])
def search_book(ISBN):
    found_book = Library.search_by_isbn(ISBN)
    if found_book:
        return jsonify(found_book)
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/delete_book/<ISBN>', methods=['DELETE'])
def delete_book(ISBN):
    try:
        Library.delete_by_isbn(ISBN)
        return jsonify({'message': 'Book deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
