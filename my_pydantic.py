
from pydantic import BaseModel, ValidationError, BaseSettings
import json
from dotenv import load_dotenv

load_dotenv()


class Settings_error(BaseSettings):
    api_key: str
    login: str
    seed: int
    err: str

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"

class Settings(BaseSettings):
    api_key: str
    login: str
    seed: int

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"


class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class User(BaseModel):
    name: str
    age: int
    address: Address


def test_ok():
    user_data = {
        "name": "John Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zip_code": "10001"
        }
    }

    user = User(**user_data)
    print(user.dict())


def test_error():
    try:
        user_data = {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York"
            }
        }

        user = User(**user_data)
        print(user.dict())
    except ValidationError as e:
        print(e.errors())


def export_to_json():
    user_data = {
        "name": "John Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zip_code": "10001"
        }
    }

    user = User(**user_data)
    print(user.json())


def read_json():
    json_data = '''
    {
        "name": "John Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zip_code": "10001"
        }
    }
    '''
    data = json.loads(json_data)
    user = User.parse_obj(data)
    print(user)

    json_data = '''
    {
        "name": "John Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zip_code": "10001"
        }
    }
    '''

    user = User.parse_raw(json_data)
    print(user)


def validate_env_variables():
    try:
        app_settings = Settings()
        print(app_settings.api_key)
        print(app_settings.login)
        print(app_settings.seed)
    except ValidationError as e:
        print(e.errors())


def validate_env_variables_error():
    try:
        app_settings = Settings_error()
        print(app_settings.api_key)
        print(app_settings.login)
        print(app_settings.seed)
    except ValidationError as e:
        print(e.errors())


validate_env_variables_error()

