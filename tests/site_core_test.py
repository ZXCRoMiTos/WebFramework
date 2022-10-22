import unittest
import sys
sys.path.append('../')
from patterns.creationals import Engine, Comment


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine = Engine

    def test_create_comment(self):
        comment = self.engine.create_comment(1, 'date', 'username', 'comment_text')
        self.assertIsInstance(comment, Comment)
        self.assertIsInstance(comment.id, int)
        self.assertIsInstance(comment.page_id, int)
        self.assertIsInstance(comment.username, str)
        self.assertIsInstance(comment.comment_text, str)
        self.assertEqual(comment.page_id, 1)
        self.assertEqual(comment.date, 'date')
        self.assertEqual(comment.username, 'username')
        self.assertEqual(comment.comment_text, 'comment_text')

    def test_create_date(self):
        date = self.engine.get_date()
        self.assertIsInstance(date, str)

    def test_get_page_of_posts(self):
        posts = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        page_number = 3
        page_size_1 = 3
        page_size_2 = 10
        page_of_posts_1 = self.engine.get_page_of_posts(posts, page_number, page_size_1)
        page_of_posts_2 = self.engine.get_page_of_posts(posts, page_number, page_size_2)
        self.assertIsInstance(page_of_posts_1, list)
        self.assertEqual(len(page_of_posts_1), page_size_1)
        self.assertNotEqual(len(page_of_posts_2), page_size_2)


if __name__ == "__main__":
    unittest.main()
