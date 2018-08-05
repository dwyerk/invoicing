#!/usr/bin/env python

import datetime
import sys
import json
from jinja2 import Template
from jinja2 import Environment, PackageLoader, select_autoescape
import pdfkit
import yaml
import argparse
import models

env = Environment(
    loader=PackageLoader('invoicer', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('invoice.html')

def main(input_file, date_start, date_end, output_file, company, payer, weekly):

    billable_days = []
    billable_weeks = {}
    with open(input_file) as jsondata:
        records = json.load(jsondata)
        for record in records:
            date_s = record['date']
            date = datetime.datetime.strptime(date_s, '%Y/%m/%d')
            record['date'] = datetime.datetime.strftime(date, '%Y-%m-%d')

            # Get beginning of week. But if it's the first week, nudge it into the correct month
            week = date.isocalendar()[1]
            first_day_of_week = date - datetime.timedelta(date.weekday())

            while first_day_of_week.month != date.month:
                first_day_of_week = first_day_of_week + datetime.timedelta(1)

            first_day_of_week_s = datetime.datetime.strftime(first_day_of_week, '%Y-%m-%d')

            # Get the end of the week. But if it's the last week, nudge it into the correct month
            last_day_of_week = date + datetime.timedelta(6 - date.weekday())

            while last_day_of_week.month != date.month:
                last_day_of_week -= datetime.timedelta(1)

            last_day_of_week_s = datetime.datetime.strftime(last_day_of_week, '%Y-%m-%d')


            if date >= date_start and date <= date_end:
                record['amount'] = record['hours'] * company.rate
                billable_days.append(record)
                w = billable_weeks.setdefault(first_day_of_week_s, {'amount': 0, 'hours': 0})
                w['amount'] += record['amount']
                w['hours'] += record['hours']
                w['contract'] = record['contract']
                w['start_date'] = first_day_of_week_s
                w['end_date'] = last_day_of_week_s


    total_hours = sum([day['hours'] for day in billable_days])
    total_due = sum([day['amount'] for day in billable_days])

    # this currently needs to be in the same directory as the other source files
    tmp = 'invoicer/templates/render-out.html'

    with open(tmp, 'w') as outf:
        outf.write(template.render(
            company=company,
            payer=payer,
            billable_days=billable_days,
            billable_weeks=billable_weeks,
            processing_date=datetime.datetime.now(),
            total_hours=total_hours,
            total_due=total_due,
            weekly=weekly
            ))

    pdfkit.from_file(tmp, output_file, options={'minimum-font-size': '23'})

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('input_file')
    ap.add_argument('date_start')
    ap.add_argument('date_end')
    ap.add_argument('output_file')
    args = ap.parse_args()
    date_start, date_end = [
        datetime.datetime.strptime(d, '%Y/%m/%d') for d in [args.date_start, args.date_end]]

    with open('config.yml') as configf:
        config = yaml.load(configf.read())

    company = config['render']['company']
    payer = config['render']['payer']
    weekly = config['render']['weekly']
    main(args.input_file, date_start, date_end, args.output_file, company, payer, weekly)
    print("Wrote pdf to: {}".format(args.output_file))
