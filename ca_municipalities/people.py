from utils import CanadianScraper, CanadianPerson as Person
from opencivicdata.divisions import Division
from pupa.scrape import Organization
import re
from utils import CSVScraper
import requests
from collections import defaultdict
import os
from io import BytesIO, StringIO
import agate
import agateexcel 
import csv
import sys
import json
import urllib.request


class CanadaMunicipalitiesPersonScraper(CSVScraper):
    csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRrGXQy8qk16OhuTjlccoGB4jL5e8X1CEqRbg896ufLdh67DQk9nuGm-oufIT0HRMPEnwePw2HDx1Vj/pub?output=csv'
    encoding = 'utf-8'
    locale = 'fr'
    corrections = {
        'district name': lambda value: value.capitalize(),
    } 
  
    def scrape(self):
        infixes = {
        'CY': 'City',
        'DM': 'District',
        'IGD': 'District',
        'IM': 'Municipal',
        'RGM': 'Regional',
        'T': 'Town',
        'VL': 'Village',
        'RDA': 'District',
        }
        exclude_districts = {}
        processed_ids = set()
        exclude_divisions = {}
        processed_divisions = set()
        print("scrape---------")
        seat_numbers = defaultdict(lambda: defaultdict(int))
        data = None

        organizations = {}
        names_to_ids = {}

        processed_ids = set()
        exclude_divisions = {}
        processed_divisions = set()
        
        for division in Division.get('ocd-division/country:ca').children('csd'):
            type_id = division.id.rsplit(':', 1)[1]
            if type_id.startswith('59'):
                if division.attrs['classification'] == 'IRI':
                    continue
                if division.name in names_to_ids:
                    names_to_ids[division.name] = None
                else:
                    names_to_ids[division.name] = division.id
          
        print("reader---------")
        reader = self.csv_reader(self.csv_url, delimiter=self.delimiter, header=True, encoding=self.encoding, skip_rows=self.skip_rows, data=data)
        reader.fieldnames = [self.header_converter(field) for field in reader.fieldnames]
        for row in reader:
            if row.get('district name'):
                municipalities = row['district name']
                print("1........................")
                print(municipalities)
       

            for municipality in municipalities:
                if row.get('district id'):
                    division_id = row['district id']
                    print("2.........")
                    print(division_id)
                if row.get('district name'):
                    division_name = row['district name']
                    print("3.........")
                    print(division_name)

                if row.get('primary role'):
                    leader_reps=row['primary role']   
                    print("4............")
                    print(leader_reps)
                    
                # organization_name = '{} {} Council'.format(division_name, infixes[division.attrs['classification']])
                if row.get('organization'):
                    organization_name = row['organization']
                    print("5...........")
                    print(organization_name)

                if row.get('source url'):
                    record_url=row['source url']   
                    print("6............")
                    print(record_url)
                print("11111111111111111111111111")
                print(division_id)

                division = Division.get('ocd-division/country:ca/csd:1308007')

                if division_id not in processed_ids:
                    processed_ids.add(division_id)
                    organizations[division_id] = Organization(name=organization_name, classification='government')
                    organizations[division_id].add_source(record_url)
                organization = organizations[division_id]
                organization.add_post(role='Mayor', label=division_name, division_id=division_id)
                organization.add_post(role='Councillor', label=division_name, division_id=division_id)

       
            if municipal_id and municipal_id.strip():
                # Get division ID from municipal name and filter out duplicates or unknowns.
                if division_name in exclude_districts or division_name in processed_divisions:
                    continue
                division_id = names_to_ids[division_name]
                if not isinstance(division_id, str):
                    continue
                if division_id in exclude_divisions:
                    continue
                if division_id in processed_ids:
                    raise Exception('unhandled collision: {}'.format(division_id))
                division = Division.get(division_id)
                processed_divisions.add(division_name)

                # Create person records for all mayor and councillor representatives.
                for leader_rep in leader_reps:
                    yield self.person_data(leader_rep, division_id, division_name, 'Mayor', organization_name)
                for councillor_rep in councillor_reps:
                    yield self.person_data(councillor_rep, division_id, division_name, 'Councillor', organization_name)

        # Iterate through each organization.
            for organization in organizations.values():
                yield organization



        def person_data(self, representative, division_id, division_name, role, organization_name):
       

            #p = Person(primary_org='government', primary_org_name=organization_name, name=representative_name, district=division_name, role=role)
            if row.get('full name'):
                representative_name = row['full name']

            p = Person(primary_org='government', primary_org_name=organization_name, name=representative_name, district=division_name, role=role)

            p.add_source(self.csv_url)

            if not row.get('district name') and row.get('district id'):  # ca_on_toronto_candidates
                if len(row['district id']) == 7:
                    p._related[0].extras['boundary_url'] = '/boundaries/census-subdivisions/{}/'.format(row['district id'])

          # p._related[0].extras['boundary_url'] = '/boundaries/census-subdivisions/{}/'.format(division_id.rsplit(':', 1)[1])
            if row.get('gender'):
                p.gender = row['gender']
            if row.get('photo url'):
                p.image = row['photo url']

            if row.get('source url'):
                p.add_source(row['source url'])

            if row.get('website'):
                p.add_link(row['website'], note='web site')
            if row.get('facebook'):
                p.add_link(re.sub(r'[#?].+', '', row['facebook']))
            if row.get('twitter'):
                p.add_link(row['twitter'])

            if row['email']:
                p.add_contact('email', row['email'].strip().split('\n')[-1])
            if lines:
                p.add_contact('address', '\n'.join(lines), 'legislature')
            if row.get('representative_phone'):
                p.add_contact('voice', row['phone'].split(';', 1)[0], 'legislature')  
            if row.get('fax'):
                p.add_contact('fax', row['fax'], 'legislature')
            if row.get('cell'):
                p.add_contact('cell', row['cell'], 'legislature')
            if row.get('birth date'):
                p.birth_date = row['birth date']

            if row.get('incumbent'):
                p.extras['incumbent'] = row['incumbent']

            # if name in self.other_names:
            #     for other_name in self.other_names[name]:
            #         p.add_name(other_name)

            return p


        # # data_list = list()
    #     division_name=[]
    #     division_id=[]
    #     organizations=[]
    #     role=[]
    #     representative_name=[]
    #     representative_phone=[]
    #     representative_email=[]
    #     for row in reader:
    #         municipalities = row.get('district name')
    #         assert len(municipalities), 'No municipalities found'


    #         division_name.append(row['district name'])

    #         district_id=row.get('district id')
    #         division_id.append(row['district id'])
            
    #         organization=row.get('organization')
    #         organizations.append(row['organization'])

    #         primary_role=row.get('primary role')
    #         role.append(row['primary role'])

        
    #         # Get name.
    #         name=row.get('full name')
    #         representative_name.append(row['full name'])

    #         # Get phone.
    #         phone = row.get('phone')
    #         representative_phone.append(row['phone'])

    #         # Get email.
    #         email = row.get('email')
    #         representative_email.append(row['email'])


    #     # for municipality in range(len(division_name)): 
    #     #     print (division_name[municipality])


    #     # for district in range(len(division_id)): 
    #     #     print (division_id[district])


    #     # for x in range(len(organizations)): 
    #     #     print (organizations[x])


    #     # for rep in range(len(role)): 
    #     #     print (role[rep])


    #     for leader_rep in role:
    #         yield self.person_data(leader_rep, division_id, division_name, 'Mayor', organizations)


    # # Iterate through each organization.
    #     for organization in organizations:
    #         yield organization


    # def person_data(self,representative_name, division_id, division_name, role, organizations):


    #     p = Person(primary_org='government', primary_org_name=organizations, name=representative_name, district=division_name, role=role)
    #     p.add_source(self.csv_url)
    #     #p._related[0].extras['boundary_url'] = url
        
        
    #     url_test = '/boundaries/census-subdivisions/%s'
    #     for i in division_id:
    #         url = url_test %i
    #         print(url)

    #     p._related[0].extras['boundary_url'] = url
    #     return p




        
