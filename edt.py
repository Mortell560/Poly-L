import requests
from pprint import pprint
import datetime
from ics import Calendar, Event
import pytz
utc=pytz.UTC

Ids_bat = {"620": [652, 832, 787, 780, 696, 736, 775, 817, 704, 712, 790, 842, 837, 819, 702, 660, 574, 741, 668]}
# Dans l'ordre: amphi, salles de pc, salles de td, salles de projets/platformes

def getEDT(id: int = 2302, dateS: datetime.date = datetime.datetime.today(), dateF: datetime.date = datetime.date(datetime.datetime.today().year, (datetime.datetime.today().month+1)%13, datetime.datetime.today().day)) -> Calendar:
    url = f"https://ade-planning.polytech.universite-paris-saclay.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources={id}&projectId=5&calType=ical&lastDate={dateF.year}-{dateF.month}-{dateF.day}&firstDate={dateS.year}-{dateS.month}-{dateS.day}"
    with requests.Session() as s:
        c = Calendar(s.get(url).text)
    #pprint(c.events)
    #for event in c.events:
    #    pprint(event.description.strip()[:-30])
    return c

def nextClass(c: Calendar, d: datetime.datetime = datetime.datetime.utcnow()) -> Event:
    d = utc.localize(d)
    temp = []
    for event in c.events:
        if event.begin.datetime >= d:
            temp.append(event)
    if len(temp) == 0:
        return None
    return min(temp, key=lambda x : x.begin.datetime)

def findCurrentlyOccupiedRooms(bats: list[str] = ["620"], d: datetime.datetime = datetime.datetime.utcnow()) -> list[str]:
    cf = Calendar()
    d = utc.localize(d)
    for bat in bats:
        for salle_id in Ids_bat[bat]:
            c = getEDT(salle_id, d, d)
            for event in c.events:
                if event.begin.datetime <= d <= event.end.datetime:
                    cf.events.add(event)
    rooms = [event.location for event in cf.events]
    rooms.sort()
    return rooms


if __name__ == "__main__":
    pprint(findCurrentlyOccupiedRooms(d=datetime.datetime(2023, 1, 9, 9, 0, 0, 0)))