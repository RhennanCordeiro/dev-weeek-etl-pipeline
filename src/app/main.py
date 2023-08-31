"""
Main file of the project
"""
import json

import openai
import pandas as pd
import requests

from .config import settings

openai.api_key = settings.get('default')['openai_api_key']
url_api = settings.get('default')['sdw_api']
def read_csv(column: str,file: str):
    """
    Generic method to read csv
    Params: column
          : file
    return: list
    """
    try:
        data_frame = pd.read_csv(file)
        return data_frame[column].tolist()
    except pd.errors.EmptyDataError:
        return "Read CSV Fail"

def get_sdw_api(user_id: int):
    """
    Get DevWeeek APi users
    """
    api_url = url_api
    response = requests.get(
        f'{api_url}/users/{user_id}',
        timeout=300
    )
    return response.json() if response.status_code == 200 else None

def list_users() -> dict:
    """
    For list users caling read_csv 
    and get_sdw_api functions
    """
    users_ids = read_csv('UserID','src/files/csv/SDW2023.csv')
    users = [user for id in users_ids if (user := get_sdw_api(id)) is not None]
    return json.dumps(users, indent=2)

def generate_ai_news(user):
    """
    For usage chatGPT for formulate
    motivacional phrase for financial
    """
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
        {
            "role": "system",
            "content": "Você é um especialista em markting bancário."
        },
        {
            "role": "user",
            "content": f"Crie uma mensagem para {user['name']} \
            sobre a importância dos investimentos (máximo de 100 caracteres)"
        }
        ]
    )
    return completion.choices[0].message.content.strip('\"')

def update_user(user):
    """
    Method for send put request to SDW api for update user with phrase
    """
    response = requests.put(f"{url_api}/users/{user['id']}", json=user,timeout=300)
    if response.status_code == 200:
        return True
    return False

def main():
    """
    Bellow code to call functions and run code
    """
    for user in list_users():
        news = generate_ai_news(user)
        print(news)
        user['news'].append({
            "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
            "description": news
        })
        status = update_user(user)
        print(f"User {user['name']} updated? {status}!")

main()
