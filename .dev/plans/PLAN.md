# PLAN

Python application that scans my google callendar for events and exports all events with requested hashtags to eather the terminal or to a file

## CLI PARAMS

-c: google calendar public location
-s: what to search for in the description (what hashtags to search for)
-d: date, dates or from/to date to filter (this should also accept times) (default is todays date)
-w: output file/filepath to write to (excel, )
-e: file format to export as (pdf, xls, xlsx, xlsb, xlsm, ods, csv, json)
-t: output to terminal (default)

## USAGE

- User calls the application providing cli configurations.
- application opens provided calendar link filters the data requested by the user
- and generates the output requested by the user