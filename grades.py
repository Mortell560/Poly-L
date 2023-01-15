import grades
from bs4 import BeautifulSoup
import requests
import datetime

months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def getGrades(LOGIN, PASSWORD):
    with requests.Session() as s:
        baseUrl = 'https://oasis.polytech.universite-paris-saclay.fr/'
        url1 = baseUrl + "prod/bo/core/Router/Ajax/ajax.php?targetProject=oasis_polytech_paris&route=BO\\Connection\\User::login"
        
        s.get(url1)
        login_data = {'login': LOGIN, 'password': PASSWORD, 'url': 'codepage=MYMARKS'}
        r = s.post(url1, data=login_data)

        url = baseUrl + 'prod/bo/core/Router/Ajax/ajax.php?targetProject=oasis_polytech_paris&route=BO\Layout\MainContent::load&codepage=MYMARKS'
        r = s.get(url)

        html = BeautifulSoup(r.text, 'html.parser').prettify()
        soup = BeautifulSoup(html, 'html.parser')
        
        courses_html = [
            course.find_parent('tr')
            for course in soup.find_all(class_="courseLine")
        ]
        
        courses = []
        for course_html in courses_html:
            course = {}
            
            # Subject and name of the grade
            course['subject-id'] = course_html.find_all('td')[0].find('div').text.splitlines()[1].strip()[:-2]
            course['subject'] = course_html.find_all('td')[0].find('div').text.splitlines()[3].strip()
            course['name'] = course_html.find_all('td')[1].text.strip()
            
            # Grade
            grade_str = course_html.find_all('td')[3].text.strip()
            try:
                course['grade'] = float(grade_str.replace(',', '.'))
            except ValueError:
                course['grade'] = None
                
            # Date and conversion to python datetime object
            course['date-str'] = course_html.find_all('td')[2].text.strip()
            date_list = course['date-str'].split(' ')
            course['date'] = datetime(int(date_list[2]), months.index(date_list[1]) + 1, int(date_list[0]))
            
            # Ranking
            
            
            courses.append(course)
        
        return courses