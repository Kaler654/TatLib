from flask import Blueprint, jsonify, make_response, request
from . import db_session
from .word_levels import Word_level
from .users import User

blueprint = Blueprint(
    'word_levels_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/word_levels', methods=["GET"])
def get_word_levels():
    db_sess = db_session.create_session()
    word_levels = db_sess.query(Word_level).all()
    return jsonify(
        {item.id: item.to_dict() for item in word_levels}
    )


@blueprint.route('/api/word_levels/<int:word_level_id>', methods=['GET'])
def get_one_word_level(word_level_id):
    db_sess = db_session.create_session()
    word_levels = db_sess.query(Word_level).get(word_level_id)
    if not word_levels:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {word_levels.id: word_levels.to_dict()}
    )


@blueprint.route('/api/word_levels', methods=['POST'])
def create_word_levels():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['word_id', 'user_id', 'word_level']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    word_level = Word_level(
        word_id=request.json['word_id'],
        user_id=request.json['user_id'],
        word_level=request.json['word_level'],
    )
    if 'date' in request.json:
        word_level.date = request.json['date']
    db_sess.add(word_level)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/word_levels/<int:word_level_id>', methods=['DELETE'])
def delete_word_level(word_level_id):
    db_sess = db_session.create_session()
    word_level = db_sess.query(Word_level).get(word_level_id)
    if not word_level:
        return jsonify({'error': 'Not found'})
    db_sess.delete(word_level)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/word_levels/<int:user_id>/<int:word_id>', methods=['PUT'])
def edit_word_level(user_id, word_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['word_id', 'user_id', 'word_level', 'date']):
        return jsonify({'error': 'Bad put request'})

    db_sess = db_session.create_session()
    word_level = db_sess.query(Word_level).filter(User.id == user_id, Word_level.word_id == word_id).first()
    if word_level:
        word_level.word_id = request.json['word_id']
        word_level.user_id = request.json['user_id']
        word_level.word_level = request.json['word_level']
        word_level.date = request.json['date']
        db_sess.commit()
        return jsonify({'success': 'OK'})
    return jsonify({'error': 'EERRERERRERERERERERER'})
