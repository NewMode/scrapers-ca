from __future__ import unicode_literals
from utils import CanadianJurisdiction
from pupa.scrape import Organization


class Saskatoon(CanadianJurisdiction):
    classification = 'legislature'
    division_id = 'ocd-division/country:ca/csd:4711066'
    division_name = 'Saskatoon'
    name = 'Saskatoon City Council'
    url = 'http://www.saskatoon.ca'
    use_type_id = True
