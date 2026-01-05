from sqlalchemy.orm import sessionmaker

from TodoApp.database import SQLALCHEMY_DATABASE_URL
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.pool import StaticPool
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass= StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def override_get_current_user():
    return {'username': 'codingwithrobytest', 'id':1, 'user_role': 'admin'}

app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title = "Learn to code!",
        description = "Need to learn everyday!",
        priority=5,
        complete = False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()



def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Learn to code!"
    assert data[0]["owner_id"] == 1


def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Learn to code!"
    assert data["owner_id"] == 1


def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo",
        "description": "New todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.post("/todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data["title"]
    assert model.description == request_data["description"]
    assert model.priority == request_data["priority"]
    assert model.complete == request_data["complete"]


