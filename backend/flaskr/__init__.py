import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

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
        try:
            question=Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            else:
                question.delete()
                selection=Question.query.order_by(Question.id).all()
                current_questions=paginate_questions(request,selection)

                return jsonify({
                    'success': True,
                    'deleted_questionID': question_id,
                    'questions': current_questions,    
                })

        except Exception:
            abort(422)
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def new_question_or_search_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        #rating = data.get('rating', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm', None)
        #print(data)

        try:

            if search:
                questions = Question.query.filter(Question.question.ilike(f'%{search}%'))
                found_questions = paginate_questions(questions)

                return jsonify({
                    'success': True,
                    'questions': found_questions
                })
            else:
                question=Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    #rating=int(rating),
                    category=new_category
                )
                question.insert()

                all_questions = Question.query.order_by(Question.id).all()
                updated_questions = paginate_questions(all_questions)
                return jsonify({
                    'success': True,
                    'created': new_question.id,
                    'questions': updated_questions,
                    'total_questions': len(all_questions)
                })
        except:
            abort(422)
                

    """"
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def categorized_questions(category_id):
        selection = Question.query.filter_by(category=category_id).all()
        current_questions = paginate_questions(request, selection)
        current_category = category_id
        return jsonify({
            'success': True,
            'questions': current_questions,
            'category': current_category
        })


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            data = request.get_json()
            previous_questions = data.get('previous_questions')
            quiz_category = data.get('quiz_category')

            current_category_questions = Question.query.filter(Question.category == quiz_category.get('id'))

            current_question = random.choice([question for question in current_category_questions if question.category not in previous_questions])

            random_question = {
                'id': current_question.id,
                'question': current_question.question, 
                'answer': current_question.answer, 
                'category': current_question.category, 
                'difficulty': current_question.difficulty
            }

            return jsonify({
                'success': True, 
                'question': random_question
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

    return app

