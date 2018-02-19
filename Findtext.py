#### Simple script used to search text from multiple python scripts##
import glob
import os
textF= "iceEffectiveDepthCtrl"
aipoll='hws-aipoll.mb.ec.gc.ca'
working1='wwghwpapp1.mb.ec.gc.ca'
stage2 ="hwp-app-stage2.to.on.ec.gc.ca"

for file in glob.glob('*.py'):
    with open(file) as f:
        contents = f.read()
    if textF in contents:
        print file
