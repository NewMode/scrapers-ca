from utils import CanadianJurisdiction


class CanadianMunicipalities(CanadianJurisdiction):
    classification = 'government'
    division_id = 'ocd-division/country:ca'
    division_name = 'Canada'
    name = 'Canada municipal councils'
    url = 'https://docs.google.com/spreadsheets/d/1QY-3q6W2edSORTgWlh8og_TJRQl1TZ3b7_Dn9E_TrMw/edit#gid=0'

    def get_organizations(self):
        return []
