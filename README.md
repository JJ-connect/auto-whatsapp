# whatsapp-sender

The following values need to be hard coded into the Python file (at present):

- NUMBER_OF_PHOTOGRAPHS
- PHOTO_COLLECT_LOCATION
- PHOTO_DEPOSIT_LOCATION
- GROUP_TO_SEND_TO

It will use the last modified date for the file as the text to go with it.
Beware relative vs absolute file paths for moving photos around.

## First time usage

Set up Python environment
Comment out the --headless line so that you can scan the QR code first time
Afterwards, replace the --headless line

## Windows Steps

1. pip install -r requirements.txt
2. run whatsapp.py

## Linux steps

1. sudo apt-get install chromium-chromedriver
2. pip install -r requirements.txt
3. run whatsapp.py
4. This can be automated using cron

## Issues

- File modified date rather than creation date
- Some manual steps required for installation
- Ungraceful error handling
- Logs aren't written out anywhere
- Inconsistent log formatting
- Contact/Group must be visible on screen (solved by pinning) else the HTML element for them won't appear
- Arbitrary waiting for file to complete sending
- Incomplete Python typing
- Incomplete Python docstrings
- Magic number of parent elements to get to a clickable element for opening chat
- Methods not collected into classes
- Untested on Mac
- chrome_options is deprecated in favour of options
- Add hard coded variables as CLI arguments
- Add help dialogue
  