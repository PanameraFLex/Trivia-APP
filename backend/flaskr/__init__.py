import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})  #Passing * 

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/categories', methods = ['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()
            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions]
            })
        except Exception as e:
            print(e)
            return json.dumps({
                'success': False,
                'error': "An error occurred"
            }), 500

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True, 
            'questions': current_questions,
            'total_questions': len(Question.query.all()), 
            'current_category': 'None',
            'categories': formatted_categories

        })
    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = \
            Question.query.filter(Question.id == question_id).one_or_none()
        if question:
            question.delete()
            return jsonify({
                'success': True,
                'deleted_id': question_id
            })

        else:
            return json.dumps({
                'success': False,
                'error': 'Not Found'
            }), 404
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        data = dict(request.form or request.json or request.data)
        new_question = Question(
            question=data.get('question'),
            answer=data.get('answer'),
            category=data.get('category'),
            difficulty=data.get('difficulty', 1))

        # Validate category before adding new question
        if not new_question.question or \
                not new_question.answer or\
                not new_question.category:
            return json.dumps({
                'success': False,
                'error': 'Missing params.'
            }), 400
        else:
            try:
                new_question.insert()
                return json.dumps(
                    {'success': True, 'question_id': new_question.id}
                ), 201
            except Exception as e:
                print(e)
                return json.dumps({
                    'success': False,
                    'error': "An error occurred"
                }), 500
                

    @app.route('/questions/find', methods=['POST'])
    def retrieve_questions_by_term():
        data = dict(request.form or request.json or request.data)
        search_term = data.get('searchTerm')

        if search_term:
            # `ilike` instead of `like` to be case-insensitive.
            questions = \
                Question.query.filter(Question.question.ilike(
                    f'%{search_term}%')
                ).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions]
            })
        else:
            return json.dumps({
                'success': False,
                'error': 'Missing params.'
            }), 400

    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():

        try:

            body = request.get_json()

            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')

            if quiz_category.get('id') == 0:
                current_category_questions = Question.query.all()
            else:
                current_category_questions = Question.query.filter(
                    Question.category == quiz_category.get('id'))

            random_question = random.choice(
                [question for question in current_category_questions if question.category not in previous_questions])

            present_question = {
                'id': random_question.id,
                'question': random_question.question,
                'answer': random_question.answer,
                'category': random_question.category,
                'difficulty': random_question.difficulty
            }

            return jsonify({
                'success': True,
                'question': present_question
            })
        except:
            abort(422)
    """""
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'

        }), 404

    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify({
            'success': 'False',
            'error': 422, 
            'message': 'Unprocessable error' 

        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Server Error"
        }), 500

    return app

