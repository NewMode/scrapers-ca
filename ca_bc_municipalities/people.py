from utils import CanadianScraper, CanadianPerson as Person

LIST_PAGE = 'https://www.civicinfo.bc.ca/people'

import re

class BritishColumbiaMunicipalitiesPersonScraper(CanadianScraper):
    def scrape(self):
        # Scrape list of municpalities.
        list_page = self.lxmlize(LIST_PAGE)
        municipalities = list_page.xpath('//select[@name="lgid"]/option')
        assert len(municipalities), 'No municipalities found'
        # Iterate through each municipality.
        for municipality in municipalities:
            municipality_text = municipality.text
            municipal_id = municipality.get('value')
            municipal_type = municipality_text[municipality_text.find('(') + 1 : municipality_text.find(')')]
            municipal_name = municipality_text.split(' (')[0]
            record_url = LIST_PAGE + '?stext=&type=ss&lgid=' + municipal_id + '&agencyid=+'
            # If we have a municipal ID, load records for that municipality.
            if municipal_id and municipal_id.strip():
                municipal_page = self.lxmlize(record_url)
                number_of_records_text = municipal_page.xpath('//main/h4/text()')
                number_of_records = int(re.search(r'\d+', number_of_records_text[0]).group())
                # Collate mayor and councillor representatives on first page of records.
                leader_reps = municipal_page.xpath('//main/ol/li[contains(., "Mayor")]')
                councillor_reps = municipal_page.xpath('//main/ol/li[contains(., "Councillor")]')
                # Iterate through additional pages of records if they exists adding reps.
                if number_of_records > 10:
                    quotient, remainder = divmod(number_of_records, 10)
                    number_of_pages = quotient + int(bool(remainder))
                    for i in range(2, number_of_pages + 1):
                        municipal_page = self.lxmlize(record_url + '&pn=' + str(i))
                        additional_leader_reps = municipal_page.xpath('//main/ol/li[contains(., "Mayor")]')
                        leader_reps.extend(additional_leader_reps)
                        additional_councillor_reps = municipal_page.xpath('//main/ol/li[contains(., "Councillor")]')
                        leader_reps.extend(additional_councillor_reps)
                # Create person records for all mayor and councillor representatives.
                for leader_rep in leader_reps:
                    yield self.person_data(leader_rep, municipal_id, municipal_type, municipal_name, 'Mayor')
                for councillor_rep in councillor_reps:
                    yield self.person_data(councillor_rep, municipal_id, municipal_type, municipal_name, 'Councillor')

    def person_data(self, representative, municipal_id, municipal_type, municipal_name, role):
        # Corrections.
        name_corrections = {
            'Claire l Moglove': 'Claire Moglove',
            'KSenya Dorwart': 'Ksenya Dorwart',
        }
        email_corrections = {
            'sharrison@qualicumbeach,com': 'sharrison@qualicumbeach.com'
        }
        # Get name.
        representative_name = re.sub(' +', ' ', str(representative.xpath('a/b/text()')[0]).strip())
        representative_name = name_corrections.get(representative_name, representative_name)
        # Get phone.
        representative_phone = str(representative.xpath('text()[contains(., "Phone")]'))[12:-2].replace('-', '')
        # Get email.
        representative_email = representative.xpath('a[contains(@href,"mailto:")]/text()')[0]
        representative_email = email_corrections.get(representative_email, representative_email)
        # Create record and append contact data.
        p = Person(primary_org='legislature', name=representative_name, district=municipal_name, role=role)
        p.add_source(LIST_PAGE)
        if representative_email:
            p.add_contact('email', representative_email)
        if representative_phone and len(representative_phone) is 10:
            p.add_contact('voice', representative_phone, 'legislature')

        return p
