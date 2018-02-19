#### Simple script used to search text from multiple python scripts##
import glob
import os
TextInNeed='EHSN_rating_curve'


for file in glob.glob('*.py'):
    with open(file) as f:
        contents = f.read()
    if TextInNeed in contents:
        print file
