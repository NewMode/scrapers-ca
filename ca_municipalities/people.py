from utils import csv_reader

class MunicipalCSVScraper(CanadianScraper):
    # File flags
    """
    Set the CSV file's delimiter.
    """
    delimiter = ','
    """
    Set the CSV file's encoding, like 'windows-1252' ('utf-8' by default).
    """
    encoding = None
    """
    If `csv_url` is a ZIP file, set the compressed file to read.
    """
    filename = None

    # Table flags
    """
    If the CSV table starts with non-data rows, set the number of rows to skip.
    """
    skip_rows = 0

    # Row flags
    """
    A dictionary of column names to dictionaries of actual to corrected values.
    """
    corrections = {}
    """
    Set whether the jurisdiction has multiple members per division, in which
    case a seat number is appended to the district.
    """
    many_posts_per_area = False
    """
    If `many_posts_per_area` is set, set the roles without seat numbers.
    """
    unique_roles = ('Mayor', 'Deputy Mayor', 'Regional Chair')
    """
    A format string to generate the district name. Rarely used.
    """
    district_name_format_string = None
    """
    A dictionary of column names to alternate column names. Rarely used.
    """
    fallbacks = {}
    """
    A dictionary of people's names to lists of alternate names. Rarely used.
    """
    other_names = {}
    """
    The classification of the organization.
    """
    organization_classification = None

    """
    Set the `locale` of the data, like 'fr'.
    """
    column_headers = {
        'fr': {
            'nom du district': 'district name',
            'identifiant du district': 'district id',
            'rôle': 'primary role',
            'prénom': 'first name',
            'nom': 'last name',
            'genre': 'gender',
            'nom du parti': 'party name',
            'courriel': 'email',
            "url d'une photo": 'photo url',
            'url source': 'source url',
            'site web': 'website',
            'adresse ligne 1': 'address line 1',
            'adresse ligne 2': 'address line 2',
            'localité': 'locality',
            'province': 'province',
            'code postal': 'postal code',
            'téléphone': 'phone',
            'télécopieur': 'fax',
            'cellulaire': 'cell',
            'facebook': 'facebook',
            'twitter': 'twitter',
            'date de naissance': 'birth date',
        },
    }

    """
    Normalizes a column header name. By default, lowercases it and replaces
    underscores with spaces (e.g. because Esri fields can't contain spaces).
    """
    def header_converter(self, s):
        header = s.lower().replace('_', ' ')
        if hasattr(self, 'locale'):
            return self.column_headers[self.locale].get(header, header)
        else:
            return header

    """
    Returns whether the row should be imported. By default, skips empty rows
    and rows in which a name component is "Vacant".
    """
    def is_valid_row(self, row):
        empty = ('', 'Vacant')
        if not any(row.values()):
            return False
        if 'first name' in row and 'last name' in row:
            return row['last name'] not in empty and row['first name'] not in empty
        return row['name'] not in empty

    def scrape(self):
        seat_numbers = defaultdict(lambda: defaultdict(int))

        extension = os.path.splitext(self.csv_url)[1]
        if extension in ('.xls', '.xlsx'):
            data = StringIO()
            binary = BytesIO(self.get(self.csv_url).content)
            if extension == '.xls':
                table = agate.Table.from_xls(binary)
            elif extension == '.xlsx':
                table = agate.Table.from_xlsx(binary)
            table.to_csv(data)
            data.seek(0)
        elif extension == '.zip':
            basename = os.path.basename(self.csv_url)
            if not self.encoding:
                self.encoding = 'utf-8'
            try:
                response = requests.get(self.csv_url, stream=True)
                with open(basename, 'wb') as f:
                    for chunk in response.iter_content():
                        f.write(chunk)
                with ZipFile(basename).open(self.filename, 'r') as fp:
                    data = StringIO(fp.read().decode(self.encoding))
            finally:
                os.unlink(basename)
        else:
            data = None

        reader = self.csv_reader(self.csv_url, delimiter=self.delimiter, header=True, encoding=self.encoding, skip_rows=self.skip_rows, data=data)
        reader.fieldnames = [self.header_converter(field) for field in reader.fieldnames]
        for row in reader:
            # ca_qc_laval: "maire et president du comite executif", "conseiller et membre du comite executif"
            # ca_qc_montreal: "Conseiller de la ville; Membre…", "Maire d'arrondissement\nMembre…"
            if row.get('primary role'):
                row['primary role'] = re.split(r'(?: (?:et)\b|[;\n])', row['primary role'], 1)[0].strip()

            if self.is_valid_row(row):
                for key, corrections in self.corrections.items():
                    if not isinstance(corrections, dict):
                        row[key] = corrections(row[key])
                    elif row[key] in corrections:
                        row[key] = corrections[row[key]]

                # ca_qc_montreal
                if row.get('last name') and not re.search(r'[a-z]', row['last name']):
                    row['last name'] = re.sub(r'(?<=\b[A-Z])[A-ZÀÈÉ]+\b', lambda x: x.group(0).lower(), row['last name'])

                if row.get('first name') and row.get('last name'):
                    name = '{} {}'.format(row['first name'], row['last name'])
                else:
                    name = row['name']

                province = row.get('province')
                role = row['primary role']

                # ca_qc_laval: "maire …", "conseiller …"
                if role not in ('candidate', 'member') and not re.search(r'[A-Z]', role):
                    role = role.capitalize()

                if self.district_name_format_string:
                    if row['district id']:
                        district = self.district_name_format_string.format(**row)
                    else:
                        district = self.jurisdiction.division_name
                elif row.get('district name'):
                    district = row['district name']
                elif self.fallbacks.get('district name'):
                    district = row[self.fallbacks['district name']] or self.jurisdiction.division_name
                else:
                    district = self.jurisdiction.division_name

                district = district.replace('–', '—')  # n-dash, m-dash

                # ca_qc_montreal
                if district == 'Ville-Marie' and role == 'Maire de la Ville de Montréal':
                    district = self.jurisdiction.division_name

                if self.many_posts_per_area and role not in self.unique_roles:
                    seat_numbers[role][district] += 1
                    district = '{} (seat {})'.format(district, seat_numbers[role][district])

                lines = []
                if row.get('address line 1'):
                    lines.append(row['address line 1'])
                if row.get('address line 2'):
                    lines.append(row['address line 2'])
                if row.get('locality'):
                    parts = [row['locality']]
                    if province:
                        parts.append(province)
                    if row.get('postal code'):
                        parts.extend(['', row['postal code']])
                    lines.append(' '.join(parts))

                organization_classification = self.organization_classification or self.jurisdiction.classification
                p = CanadianPerson(primary_org=organization_classification, name=name, district=district, role=role, party=row.get('party name'))
                p.add_source(self.csv_url)

                if not row.get('district name') and row.get('district id'):  # ca_on_toronto_candidates
                    if len(row['district id']) == 7:
                        p._related[0].extras['boundary_url'] = '/boundaries/census-subdivisions/{}/'.format(row['district id'])

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
                    p.add_contact('email', row['email'].strip().split('\n')[-1])  # ca_qc_montreal
                if lines:
                    p.add_contact('address', '\n'.join(lines), 'legislature')
                if row.get('phone'):
                    p.add_contact('voice', row['phone'].split(';', 1)[0], 'legislature')  # ca_qc_montreal, ca_on_huron
                if row.get('fax'):
                    p.add_contact('fax', row['fax'], 'legislature')
                if row.get('cell'):
                    p.add_contact('cell', row['cell'], 'legislature')
                if row.get('birth date'):
                    p.birth_date = row['birth date']

                if row.get('incumbent'):
                    p.extras['incumbent'] = row['incumbent']

                if name in self.other_names:
                    for other_name in self.other_names[name]:
                        p.add_name(other_name)

                yield p
