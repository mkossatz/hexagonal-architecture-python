from datetime import datetime, timedelta
from unittest.mock import Mock

import inject
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockFixture

from hex.domain.actions.get_post import GetPost, PostNotFound
from hex.domain.actions.search_posts import SearchPosts
from hex.domain.post import Post
from hex.web.routes.post import create_post_router, create_post_error_handlers
from hex.web.error_handlers import inject_error_handlers, create_default_error_handlers
from hex.web.responses import create_error_response


@pytest.fixture
def get_post(mocker: MockFixture) -> Mock:
    return mocker.patch('hex.web.routes.post.GetPost')


@pytest.fixture
def search_posts(mocker: MockFixture) -> Mock:
    return mocker.patch('hex.web.routes.post.SearchPosts')


@pytest.fixture
def injector(get_post: Mock, search_posts: Mock) -> None:
    inject.clear_and_configure(lambda binder: binder
                               .bind(GetPost, get_post)
                               .bind(SearchPosts, search_posts))


@pytest.fixture
def client(injector: None) -> TestClient:
    app = FastAPI()
    app.include_router(create_post_router())
    app = inject_error_handlers(app, create_post_error_handlers())
    app = inject_error_handlers(app, create_default_error_handlers())
    return TestClient(app)


@pytest.fixture
def post() -> Post:
    return Post(id=1,
                author_name='Alex',
                title='Test Post',
                body='A longer body for this post',
                created_at=datetime.now(),
                updated_at=datetime.now() + timedelta(hours=1))


class TestPostBlueprint:
    def test_list_searches_posts(self, search_posts: Mock, client: TestClient,
                                 post: Post) -> None:
        search_posts.execute.return_value = [post], 100

        response = client.get('/posts')

        search_posts.execute.assert_called_once_with(start_after=None, end_before=None)

        assert response.json()['count'] == 100
        assert len(response.json()['results']) == 1
        result = response.json()['results'][0]
        assert result['id'] == post.id
        assert result['authorName'] == 'Alex'
        assert result['title'] == 'Test Post'
        assert result['body'] == 'A longer body for this post'
        # assert result['createdAt'] == post.created_at.isoformat()
        # assert result['updatedAt'] == post.updated_at.isoformat()

    def test_post_list_parses_query_string(self, search_posts: Mock, client: TestClient,
                                           post: Post) -> None:
        search_posts.execute.return_value = [post], 100

        client.get('/posts?start_after=10&end_before=100')

        search_posts.execute.assert_called_once_with(start_after=10, end_before=100)

    def test_detail_gets_post(self, get_post: Mock, client: TestClient, post: Post) -> None:
        get_post.execute.return_value = post

        response = client.get('/posts/1')

        get_post.execute.assert_called_once_with(post_id=1)

        assert response.json()['id'] == post.id
        assert response.json()['authorName'] == 'Alex'
        assert response.json()['title'] == 'Test Post'
        assert response.json()['body'] == 'A longer body for this post'
        # assert response.json()['createdAt'] == post.created_at.isoformat()
        # assert response.json()['updatedAt'] == post.updated_at.isoformat()

    def test_not_found_gets_post(self, get_post: Mock, client: TestClient, post: Post) -> None:
        get_post.execute.side_effect = PostNotFound(post.id)

        response = client.get('/posts/1')

        get_post.execute.assert_called_once_with(post_id=1)
        assert response.status_code == 404

        expected_response = create_error_response(
            404, 'Post Not Found',
            ['path', 'post_id'], 'A post with the id 1 does not exist',
            '/posts/1')
        assert response.json() == expected_response.to_dict()
        """
        assert response.json()['status'] == 404
        assert response.json()['title'] == 'Post Not Found'
        # assert response.json()['timestamp'] == datetime.now().isoformat()
        assert response.json()['path'] == '/posts/1'
        assert response.json()['detail'] == Detail(
            ['path', 'post_id'], 'A post with the id 1 does not exist')
        """
