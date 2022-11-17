from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = 'Equity Calculator API'
    API_V1_STR = '/api/v1'

    DATE_FORMAT = '%d-%m-%Y'

    CONTACT_NAME = 'Sergey Buchko'
    CONTACT_EMAIL = 'cep.buch@gmail.com'


settings = Settings()
