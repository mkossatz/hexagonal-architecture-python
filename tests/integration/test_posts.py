import inject
import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy import literal_column
from sqlalchemy.engine import Connection

from hex.adapters.database.postgres import posts
from hex.asgi import create_application
from hex.domain.post import Post
from hex.web.responses import create_error_response
from datetime import datetime


@pytest.fixture
def client() -> TestClient:
    inject.clear()
    app = create_application()
    return TestClient(app)


@pytest.fixture
def post(database_connection: Connection) -> Post:
    insert = posts.insert().values(author_name='aaa',
                                   title='bbb',
                                   body='ccc'
                                   ).returning(literal_column('*'))
    cursor = database_connection.execute(insert)
    result = cursor.fetchone()
    return Post(**result)


class TestPosts:
    def test_post_search_searches_posts(self, client: TestClient, post: Post) -> None:
        response = client.get('/posts')
        assert response.json()['count'] == 1
        assert len(response.json()['results']) == 1
        result = response.json()['results'][0]
        assert result['id'] == post.id
        assert result['authorName'] == 'aaa'
        assert result['title'] == 'bbb'
        assert result['body'] == 'ccc'
        # assert result['createdAt'] == post.created_at.isoformat()
        # assert result['updatedAt'] == post.updated_at.isoformat()
        """
        assert response.json() == {
            'count': 1,
            'results': [{
                'id': post.id,
                'authorName': 'aaa',
                'title': 'bbb',
                'body': 'ccc',
                'createdAt': post.created_at.isoformat(),
                'updatedAt': post.updated_at.isoformat()
            }]
        }
        """

    def test_post_detail(self, client: TestClient, post: Post) -> None:
        response = client.get(f'/posts/{post.id}')
        assert response.json()['id'] == post.id
        assert response.json()['authorName'] == 'aaa'
        assert response.json()['title'] == 'bbb'
        assert response.json()['body'] == 'ccc'
        # assert response.json()['createdAt'] == post.created_at.isoformat()
        # assert response.json()['updatedAt'] == post.updated_at.isoformat()

    def test_post_detail_not_found(self, client: TestClient, post: Post) -> None:
        response = client.get(f'/posts/100')
        assert response.status_code == 404
        expected_response = create_error_response(
            404, 'Post Not Found',
            ['path', 'post_id'], 'A post with the id 100 does not exist',
            '/posts/100')
        assert response.json() == expected_response.to_dict()
