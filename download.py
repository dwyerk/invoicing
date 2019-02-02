#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
import sys
import json
import yaml
import models

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

def main(output, spreadsheet_id, range_name):
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        records = []
        header = None
        for row in values:
            if not header:
                header = [x.lower() for x in row]
            else:
                newrow = []
                for field in row:
                    try:
                        field = float(field)
                    except ValueError:
                        pass
                    newrow.append(field)
                rec = dict(zip(header, newrow))
                rec['type'] = range_name
                records.append(rec)

        json.dump(records, output, indent=4)

if __name__ == '__main__':
    # The ID and range of a sample spreadsheet.
    with open('config.yml') as configf:
        config = yaml.load(configf)
    spreadsheet_id = config['download']['spreadsheet_id']

    timesheet_range = config['download']['timesheet_range']
    expenses_range = config['download']['expenses_range']
    with open(sys.argv[1], 'w') as output:
        main(output, spreadsheet_id, timesheet_range)
    with open(sys.argv[2], 'w') as output:
        main(output, spreadsheet_id, expenses_range)
