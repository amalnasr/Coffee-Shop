import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():

    # Get all drinks from DB
    drinks = Drink.query.all()
    
    drinks_detail = [drink.short() for drink in drinks]
    
    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks_detail
    }), 200
  

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):

    try:
        # Get all drinks from DB
        drinks = Drink.query.all()
        drinks_detail = [drink.long() for drink in drinks]

        if len(drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks_detail
        }), 200

    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):

    try:

        body = request.get_json()
        drink_name = body['title']
        drink_recipe = body['recipe']

        # if type(drink_recipe) is dict:
        #   drink_recipe = [drink_recipe]

        new_drink = Drink(title=drink_name,
                          recipe=json.dumps(drink_recipe)
                          )

        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        }), 200

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(jwt, drink_id):

    # Get the drink  by the given id
    drink = Drink.query.filter(
        Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:

        body = request.get_json()

        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    # Get the drink  by the given id
    drink = Drink.query.filter(
        Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink_id
        }), 200

    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response

