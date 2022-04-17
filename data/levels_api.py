from flask import Blueprint, jsonify, make_response, request
from . import db_session
from .levels import Level

blueprint = Blueprint(
    'levels_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/levels', methods=["GET"])
def get_levels():
    db_sess = db_session.create_session()
    levels = db_sess.query(Level).all()
    return jsonify(
        {item.id: item.to_dict() for item in levels}
    )


@blueprint.route('/api/levels/<int:level_id>', methods=['GET'])
def get_one_level(level_id):
    db_sess = db_session.create_session()
    level = db_sess.query(Level).get(level_id)
    if not level:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {level.id: level.to_dict()}
    )


@blueprint.route('/api/levels', methods=['POST'])
def create_level():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['name']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    level = Level(
        name=request.json['name']
    )
    db_sess.add(level)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/levels/<int:level_id>', methods=['DELETE'])
def delete_level(level_id):
    db_sess = db_session.create_session()
    level = db_sess.query(Level).get(level_id)
    if not level:
        return jsonify({'error': 'Not found'})
    db_sess.delete(level)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/levels/<int:level_id>', methods=['PUT'])
def edit_level(level_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['name']):
        return jsonify({'error': 'Bad put request'})

    db_sess = db_session.create_session()
    level = db_sess.query(Level).filter(Level.id == level_id).first()
    if level:
        level.name = request.json['name']
        db_sess.commit()
        return jsonify({'success': 'OK'})
    return jsonify({'error': 'EERRERERRERERERERERER'})
