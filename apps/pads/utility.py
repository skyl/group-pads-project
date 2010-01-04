from hashlib import md5
from django.template.defaultfilters import slugify

def create_pad_guid(title):
    question = slugify(title)
    return md5(question).hexdigest()
