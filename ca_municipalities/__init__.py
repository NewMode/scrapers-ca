from utils import CanadianJurisdiction
from pupa.scrape import Organization


class CanadaMunicipalities(CanadianJurisdiction):
    classification = "government"
    division_id = "ocd-division/country:ca"
    division_name = 'Canada'
    name = "Canadian municipal councils"
    url = "https://docs.google.com/spreadsheets/d/1QY-3q6W2edSORTgWlh8og_TJRQl1TZ3b7_Dn9E_TrMw/edit#gid=0"
    #csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRrGXQy8qk16OhuTjlccoGB4jL5e8X1CEqRbg896ufLdh67DQk9nuGm-oufIT0HRMPEnwePw2HDx1Vj/pub?output=csv'
    #url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRrGXQy8qk16OhuTjlccoGB4jL5e8X1CEqRbg896ufLdh67DQk9nuGm-oufIT0HRMPEnwePw2HDx1Vj/pub?output=csv'
    #url = 'https://fcm.ca/en'



    def get_organizations(self):
        return []

    # def get_organizations(self):
    # 	organization = Organization(self.name, classification=self.classification)

    #     yield organization


  # classification = 'government'
  #   division_id = 'ocd-division/country:ca/province:nb'
  #   division_name = 'New Brunswick'
  #   name = 'New Brunswick municipal councils'
  #   url = 'http://www2.gnb.ca/content/gnb/en/departments/elg/local_government/content/community_profiles.html'

  #   def get_organizations(self):
  #       return []



    # def get_organizations(self):
    #     #REQUIRED: define an organization using this format
    #     #where org_name is something like Seattle City Council
    #     #and classification is described here:
    #     org = Organization(name="org_name", classification="legislature")

    #     # OPTIONAL: add posts to your organizaion using this format,
    #     # where label is a human-readable description of the post (eg "Ward 8 councilmember")
    #     # and role is the position type (eg councilmember, alderman, mayor...)
    #     # skip entirely if you're not writing a people scraper.
    #     org.add_post(label="position_description", role="position_type")

    #     #REQUIRED: yield the organization
    #     yield org



