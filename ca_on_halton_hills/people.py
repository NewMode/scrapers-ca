from utils import CSVScraper

from datetime import date


class HaltonHillsPersonScraper(CSVScraper):
    csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQm4XOsbbuoxSX8fAFo5mLMmNK3W7oWDqHozy7uxaBUj-LdIyu9-sEeGwRi-C4i49FzqcgiZ3U1ZhpU/pub?gid=901460662&single=true&output=csv'
    created_at = date(2017, 11, 8)
    contact_person = 'andrew@newmode.net, shamus@newmode.net'
