from flask import Blueprint, jsonify, make_response, request
from . import db_session
from .users import User

blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users', methods=["GET"])
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {item.id: item.to_dict(only=('name', 'email', 'telegram_id', 'created_date', 'status', 'level_id', 'words',))
         for item in users}
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {user.id: user.to_dict(only=('name', 'email', 'telegram_id', 'created_date', 'status', 'level_id', 'words',))}
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'email', 'password']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = User(
        name=request.json['name'],
        email=request.json['email'],
    )
    user.set_password(request.json['password'])
    if 'telegram_id' in request.json:
        user.telegram_id = request.json['telegram_id']
    if 'status' in request.json:
        user.status = request.json['status']
    if 'level_id' in request.json:
        user.level_id = request.json['level_id']
    if 'words' in request.json:
        user.words = request.json['words']
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    print(user_id)
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'email']):
        return jsonify({'error': 'Bad put request'})

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user:
        user.name = request.json['name']
        user.email = request.json['email']
        if 'telegram_id' in request.json:
            user.telegram_id = request.json['telegram_id']
        if 'status' in request.json:
            user.status = request.json['status']
        if 'level_id' in request.json:
            user.level_id = request.json['level_id']
        if 'words' in request.json:
            user.words = request.json['words']
        db_sess.commit()
        return jsonify({'success': 'OK'})
    return jsonify({'error': 'EERRERERRERERERERERER'})
