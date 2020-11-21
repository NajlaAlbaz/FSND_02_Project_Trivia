import os
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]

    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @DONE: Set up CORS.
    Allow '*' for origins. Delete the sample route after completing the DONEs
    '''
    CORS(app)

    '''
    @DONE: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    '''
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
        formatted_categories = {
            category.id: category.type for category in categories
            }

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    '''
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
    of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = paginate_questions(request, questions)

        if len(formatted_questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(questions),
                'current_category': None,
                'categories': {
                    category.id: category.type for category in
                    Category.query.order_by(Category.type).all()
                        }
            })

    '''
    @DONE: Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.This removal will persist in
    the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id
                ).one_or_none()
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception:
            abort(422)

    '''
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page of the questions list in
    the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def add_questions():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            new_question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
                )
            new_question.insert()

            return jsonify({
                'success': True,
                'created': new_question.id
            })

        except Exception:
            abort(422)

    '''
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        query = body.get('searchTerm', None)

        try:
            questions = Question.query.filter(
                Question.question.ilike('%'+query+'%')
            ).all()
            formatted_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'search_term': query,
                'total_questions': len(questions),
                'questions': formatted_questions,
                'current_category': None
            })
        except Exception:
            abort(422)

    '''
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': category_id
            })
        except Exception:
            abort(404)

    '''
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        try:
            body = request.get_json()
            prevQuestions = body.get('previous_questions', None)
            category = body.get('quiz_category', None)

            if category['id'] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(prevQuestions)
                ).all()
            else:
                questions = Question.query.filter_by(
                    category=category['id']
                    ).filter(
                        Question.id.notin_(prevQuestions)
                    ).all()

            formatted_questions = [question.format() for question in questions]

            current_question = formatted_questions[
                random.randrange(
                    0,
                    len(formatted_questions)
                    )
                ] if len(formatted_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': current_question
            })
        except Exception:
            abort(422)

    '''
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    return app
