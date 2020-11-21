import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from decouple import config
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(config('USERNAME'), config('PASSWORD'),'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'A question',
            'answer': 'an answer',
            'difficulty': 3,
            'category': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Test get categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        pass

    def test_get_paginated_questions(self):
        """Test get paginated questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        pass

    def test_get_paginated_questions_past_valid_page(self):
        """Test get paginated questions past valid page"""
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')
        pass

    def test_get_questions_from_category(self):
        """Test get questions from specified category"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        pass

    def test_get_questions_from_nonexistant_category(self):
        """Test get error from getting questions from nonexistant category"""
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')
        pass

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        pass

    def test_delete_question(self):
        new_question = Question(
            question='A question',
            answer='an answer',
            difficulty=3,
            category=1
            )
        new_question.insert()

        res = self.client().delete(f'/questions/{new_question.id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==new_question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_question.id)
        self.assertEqual(question, None)
        pass

    def test_422_error_when_delete_nonexistant_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        pass

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'what'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
        pass

    def test_search_question_not_found(self):
        res = self.client().post('/questions/search', json={'searchTerm': '1234'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(len(data['questions']))
        self.assertFalse(data['total_questions'])
        self.assertEqual(data['current_category'], None)
        pass

    def test_get_quizzes(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 0}, 'previous_questions': []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()