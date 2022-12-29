import requests
from bs4 import BeautifulSoup
import pymongo

def scrape_jeopardy():
  # Set the base URL for the Jeopardy episode
    base_url = f"https://j-archive.com/showgame.php?game_id=6316"
    
    # Use the requests library to fetch the HTML from the Jeopardy episode page
    response = requests.get(base_url)

    # Use the BeautifulSoup library to parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all of the table cells that contain the questions
    cells = soup.find_all('td', class_='clue')

    # Iterate through each cell and extract the question text
    questions = []
    for cell in cells:
        question = cell.find('td', class_='clue_text').text
        isDouble = False if (cell.find('td', class_='clue_value_daily_double') == None) else True
        questions.append({
            "question": question,
            "isDouble": isDouble,
        })
        
    
    cells = soup.find_all('td', class_='category')

    categories = []
    for cell in cells:
        category = cell.find('td', class_='category_name').text
        categories.append(category)

  
    return questions, categories

questions, categories = scrape_jeopardy()


for questionIdx in range(len(questions)-1):
    questions[questionIdx]['value'] = (int(questionIdx / 6) + 1) * (200 if questionIdx < int(len(questions)/2) else 400) - (0 if questionIdx < int(len(questions)/2) else 2000)
    questions[questionIdx]['round'] = 'first' if questionIdx < int(len(questions)/2) else 'second'
    questions[questionIdx]['category'] = categories[questionIdx % 6] if questionIdx < int(len(questions)/2) else categories[(questionIdx % 6) + 6]
    questions[questionIdx]['categoryCol'] = questionIdx % 6

questions[60]['category'] = categories[-1]
questions[60]['round'] = 'final'

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jeopardy"]
mycol = mydb["questions"]


for question in questions:
    mycol.insert_one(question)

