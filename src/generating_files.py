# import static_data
import datetime
import gzip
import json
import os
import urllib.request
from io import StringIO
from urllib.parse import urlparse

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/spreadsheets.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def getService():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    return service


def writeCell(service, range_, val):
    # TODO: Update placeholder value.
    spreadsheet_id = '1lonkzrZ6KaWJ0oFgTF_i6AnBVRVeCMXnVqI-mh-jVgA'

    # The A1 notation of the values to update.

    value_range_body = {
        'range': range_,
        'values': [
            [val]
        ]
    }

    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_,
        body=value_range_body,
        valueInputOption='RAW'
    )

    response = request.execute()


def readEntriesSpreadsheet(service):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    spreadsheetId = '1lonkzrZ6KaWJ0oFgTF_i6AnBVRVeCMXnVqI-mh-jVgA'
    rangeName = 'Form Responses 1!A1:P'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return None
    else:
        return values


class headers(object):
    def __init__(self, column_names):
        # ['Timestamp', 'Title', 'video', 'run_type', 'platform', 'patch_version',
        # 'date', 'quest', 'runner1', 'weapons', 'runner2', 'runner3', 'runner4', 'status']

        self.timestamp_col = column_names.index('Timestamp')
        self.title_col = column_names.index('Title')
        self.video_col = column_names.index('video')
        self.video_type = column_names.index('video_type')
        self.run_type_col = column_names.index('run_type')
        self.platform_col = column_names.index('platform')
        self.patch_version_col = column_names.index('patch_version')
        self.date_col = column_names.index('date')
        self.time_col = column_names.index('time')
        self.quest_col = column_names.index('quest')
        self.runner1_col = column_names.index('runner1')
        self.weapons_col = column_names.index('weapons')
        self.runner2_col = column_names.index('runner2')
        self.runner3_col = column_names.index('runner3')
        self.runner4_col = column_names.index('runner4')
        self.status_col = column_names.index('status')


class run(object):
    def __init__(self, entry, spreadsheet_headers):
        self.timestamp = entry[spreadsheet_headers.timestamp_col]
        self.title = entry[spreadsheet_headers.title_col]
        self.video_link = entry[spreadsheet_headers.video_col]
        self.video_type = entry[spreadsheet_headers.video_type]
        self.run_type = entry[spreadsheet_headers.run_type_col]
        self.platform = entry[spreadsheet_headers.platform_col]
        self.patch_version = entry[spreadsheet_headers.patch_version_col]
        self.date_txt = entry[spreadsheet_headers.date_col]
        self.time = entry[spreadsheet_headers.time_col]
        self.quest = entry[spreadsheet_headers.quest_col]
        self.runner1 = entry[spreadsheet_headers.runner1_col]
        self.weapons_txt = entry[spreadsheet_headers.weapons_col]
        self.runner2 = entry[spreadsheet_headers.runner2_col]
        self.runner3 = entry[spreadsheet_headers.runner3_col]
        self.runner4 = entry[spreadsheet_headers.runner4_col]
        self.status = entry[spreadsheet_headers.status_col]

        self.parseWeapon()
        self.parseDate()

    def parseWeapon(self):
        # 'great-sword, long-sword, sword-and-shield'
        self.weapons = self.weapons_txt.split(', ')

    def parseDate(self):
        # '7/17/2019'
        self.date = datetime.datetime.strptime(
            self.date_txt, '%m/%d/%Y').date().isoformat()

    def output2File(self):
        # ---
        # title          :
        # video          : https://www.youtube.com/embed/EXAMPLE
        # video_type     : youtube
        # run_type       : freestyle
        # platform       : ps4
        # patch_version  :
        # date           : 2019-01-01
        # time           : 09'99"99
        # quest          : 8★-blue-prominence

        # runners:
        #     - jin-furai
        #     - tsc

        # weapons:
        #     - great-sword
        #     - long-sword
        #     - sword-and-shield
        #     - dual-blades
        #     - hammer
        #     - hunting-horn
        #     - lance
        #     - gunlance
        #     - switch-axe
        #     - charge-blade
        #     - insect-glaive
        #     - bow
        #     - light-bowgun
        #     - heavy-bowgun
        # ---

        # yyyy-mm-dd--weapon--quest-name.md
        file_name = 'files/{}--{}--{}.md'.format(self.date, self.weapons_txt, self.quest)

        with open(file_name, "w") as f:
            f.write('---\n')
            f.write('title          : {}\n'.format(self.title))
            f.write('video          : {}\n'.format(self.video_link))
            f.write('video_type     : {}\n'.format(self.video_type))
            f.write('run_type       : {}\n'.format(self.run_type))
            f.write('platform       : {}\n'.format(self.platform))
            f.write('patch_version  : {}\n'.format(self.patch_version))
            f.write('date           : {}\n'.format(self.date))
            f.write("time           : {}\n".format(self.time))
            f.write('quest          : {}\n'.format(self.quest))
            f.write('\n')
            f.write('runners:\n')

            if self.runner1 != '':
                f.write('    - {}\n'.format(self.runner1))
            if self.runner2 != '':
                f.write('    - {}\n'.format(self.runner2))
            if self.runner3 != '':
                f.write('    - {}\n'.format(self.runner3))
            if self.runner4 != '':
                f.write('    - {}\n'.format(self.runner4))

            f.write('')
            f.write('weapons:\n')
            for weapon in self.weapons:
                f.write('    - {}\n'.format(weapon))

            f.write('---')


def processRuns(service):
    entries_from_spreadsheet = readEntriesSpreadsheet(service)
    spreadsheet_headers = headers(entries_from_spreadsheet[0])


    for i, row in enumerate(entries_from_spreadsheet):
        if i == 0:
            continue
        run(row, spreadsheet_headers).output2File()

    return spreadsheet_headers


service = getService()
processRuns(service)
