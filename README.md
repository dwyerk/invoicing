# Primitive Types Invoicing
This project is an example of how to generate invoices using Google Spreadsheets as a timesheet keeping system and jinja templates
to format the invoice.
## Getting started
Create a config.yml using config.yml.example as a base. These values will be used when rendering the invoice. For example:
```
render:
  company:
    !company
      address: 123 Main St
      name: Kevin Dwyer
      phone: 301-555-1212
      rate: 200

  payer:
    !payer
      address: 456 Business Place
      name: Widgets, Inc.
      phone: 215-555-1212

  weekly: True

download:
  spreadsheet_id: $GOOGLE_SHEET_ID_HERE
  range: Log
  range: Expenses
```

This will give `download.py` the spreadsheet ID to use to find timesheet entries. The entries will be in the Log sheet, expenses in
the Expenses sheet. It will also fill in the blanks for `render.py` for names and addresses.

Finally, run the invoice. First, download the data you want to invoice, then render the invoice into pdf for the specific time range.
```
pipenv run ./download.py 2019-01-timesheet.json 2019-01-expenses.json
pipenv run ./render.py 2019-01-timesheet.json 2019-01-expenses.json 2019/1/1 2019/1/31 invoice.pdf
open invoice.pdf
```
