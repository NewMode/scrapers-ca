from __future__ import unicode_literals
from utils import CanadianJurisdiction
from pupa.scrape import Organization


class Oshawa(CanadianJurisdiction):
    classification = 'legislature'
    division_id = 'ocd-division/country:ca/csd:3518013'
    division_name = 'Oshawa'
    name = 'Oshawa City Council'
    url = 'http://www.oshawa.ca'

    def get_organizations(self):
        organization = Organization(self.name, classification=self.classification)

        organization.add_post(role='Mayor', label='Oshawa', division_id=self.division_id)
        for i in range(1, 8):
            organization.add_post(role='Regional Councillor', label='Oshawa (seat {})'.format(i), division_id=self.division_id)
        for i in range(1, 4):
            organization.add_post(role='Councillor', label='Oshawa (seat {})'.format(i), division_id=self.division_id)

        yield organization
