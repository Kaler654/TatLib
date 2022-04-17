from flask import Blueprint, jsonify, make_response, request
from . import db_session
from .books import Book

blueprint = Blueprint(
    'books_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/books', methods=["GET"])
def get_books():
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
    return jsonify(
        {item.id: item.to_dict() for item in books}
    )


@blueprint.route('/api/books/<int:book_id>', methods=['GET'])
def get_one_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    if not book:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {book.id: book.to_dict()}
    )


@blueprint.route('/api/books', methods=['POST'])
def create_book():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['pages', 'title', 'level_id', 'user_author_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    book = Book(
        title=request.json['title'],
        pages=request.json['pages'],
        level_id=request.json['level_id'],
        user_author_id=request.json['user_author_id']
    )
    if 'author' in request.json:
        book.author = request.json['author']
    db_sess.add(book)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_job(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    if not book:
        return jsonify({'error': 'Not found'})
    db_sess.delete(book)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/books/<int:book_id>', methods=['PUT'])
def edit_job(book_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['author', 'user_author_id', 'pages', 'title', 'level_id']):
        return jsonify({'error': 'Bad put request'})

    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if book:
        book.author = request.json['author']
        book.user_author_id = request.json['user_author_id']
        book.pages = request.json['pages']
        book.title = request.json['title']
        book.level_id = request.json['level_id']
        db_sess.commit()
        return jsonify({'success': 'OK'})
    return jsonify({'error': 'EERRERERRERERERERERER'})
