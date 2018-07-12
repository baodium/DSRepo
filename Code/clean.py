import json
import re
import dateparser
from googleapiclient.discovery import build

# normalize date
API_KEY='AIzaSyCdOGjynFqrd5A-gkKKeYjqs0UIMP7FGjc'
service = build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

# clean description
def clean_desc(text):
    ind = text.index('\n')
    text = text[ind:]
    text = re.sub(r"http\S+", "", text).replace('\n','')
    text = re.sub(r'[^\w\s]' , '' , text)
    return text

# normalize date
def normalize_date(datetime):
    dateObj = dateparser.parse(datetime)
    date = dateObj.strftime('%Y-%m-%d %H:%M:%S') if dateObj is not None else ''
    return date

# find category
def find_category(s):
    try:
        start = s.index('Category') + len('Category')
        end = s.index('License', start )
        return s[start:end]
    except ValueError:
        return ""


# read json file
with open('commentVideo.json') as f:
    data = json.load(f)

output = []

for x in data:
    video = {}

    video['video_id'] = x['video_id']

    try:
        desc = clean_desc(x['description'])
        cat_str = 'Category' + find_category(desc) + 'LicenseStandard YouTube License'
        video['description'] = desc.replace(cat_str,'')
    except:
        video['description'] = ''

    try:
        video['date'] = normalize_date(x['description'][13:25])
    except:
        video['date'] = ''
    
    try:
        analyze_request = {
                    'comment': { 'text': video['description']  },
                    'requestedAttributes': {'TOXICITY': {}}
                }  
        probability = service.comments().analyze(body=analyze_request).execute()
        video['probability'] = probability['attributeScores']['TOXICITY']['summaryScore']['value']

    except:
        video['probability'] = 0.0

    video['category'] = find_category(desc)

    output.append(video)

    output_sorted = sorted(output, key=lambda k: k['probability'])

# write json file
with open('data.json', 'w+') as outfile:
    json.dump(output_sorted, outfile)