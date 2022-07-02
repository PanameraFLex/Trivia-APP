import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))



    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['categories'])

    def test_invalid_request(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_retrieve_questions_by_category(self):
        res = self.client().get('/categories/{}/questions'.format(1))
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)

    def test_retrieve_questions_by_category_fail(self):
        res = self.client().get('categories/1xx/questions')
        self.assertEqual(res.status_code, 404)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_get_questions_fail(self):
        res = self.client().get('/questions?page=1000', json={'rating': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_create_question(self):
        data = {
            'question': 'Who discovered electricity?',
            'answer': 'Thomas Edison',
            'difficulty': 3,
            'category': 1
        }
        res = self.client().post('/questions', json=data)
        self.assertEqual(res.status_code, 201)

    def test_create_question_fail(self):
        data = {
            'question': 'Who discovered electricity?',
            'answer': 'Thomas Edison',
            'difficulty': 3,
        }
        res = self.client().post('/questions', json=data)
        self.assertEqual(res.status_code, 400)

    def test_retrieve_questions_by_term(self):
        search_term = {'searchTerm': 'Egypt'}
        res = self.client().post('/questions/find', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_retrieve_questions_by_term_fail(self):
        res = self.client().post('/questions/find')
        self.assertEqual(res.status_code, 400)

    def test_delete_question(self):
        question = {
            'question': 'xxx',
            'answer': 'y',
            'difficulty': 1,
            'category': 1
        }
        operational_res = self.client().post('/questions', json=question)
        result_data = json.loads(operational_res.data)

        res = self.client().delete(
            '/questions/{}'.format(result_data.get('question_id'))
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('deleted_id'), (result_data.get('question_id')))
        self.assertTrue(data.get('success'))

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/1000')
        self.assertEqual(res.status_code, 404)
        

    def test_play_quizzes(self):
        data = {
            "previous_questions": [],
            "quiz_category": {"type": "Science", "id": "1"}
        }
        res = self.client().post('/quizzes', json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_play_quizzes_fail(self):
        res = self.client().post('/quizzes/1',)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()