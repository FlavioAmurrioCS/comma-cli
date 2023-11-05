from __future__ import annotations

# from datetime import datetime

# from faker import Faker
# from polyfactory.factories.pydantic_factory import ModelFactory
# from pydantic import BaseModel
# from pydantic import PositiveInt


# class User(BaseModel):
#     id: int
#     name: str = 'John Doe'
#     signup_ts: datetime | None
#     tastes: dict[str, PositiveInt]

# # Generate a factory function for the User Model


# class UserFactory(ModelFactory[User]):
#     __model__ = User
#     __faker__ = Faker()
#     ...
#     # class Meta:
#     #     model = User

#     @classmethod
#     def name(cls):
#         return cls.__faker__.first_name()


# for i in range(10):
#     print(UserFactory.build().model_dump_json(indent=2))


# # external_data = {
# #     'id': 123,
# #     'signup_ts': '2019-06-01 12:22',
# #     'tastes': {
# #         'wine': 9,
# #         b'cheese': 7,
# #         'cabbage': '1',
# #     },
# #     'Something': 'else'
# # }

# # user = User(**external_data)
# # print(user.id)
# # # > 123
# # print(user.model_dump())
# # """
# # {
# #     'id': 123,
# #     'name': 'John Doe',
# #     'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
# #     'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
# # }
# # """


# # print(json.dumps(user.model_json_schema(), indent=2))
