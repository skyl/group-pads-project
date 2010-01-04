from django.forms import ModelForm

from pads.models import Pad, TextArea


class PadForm(ModelForm):
    class Meta:
        model = Pad
        fields = ["title"]

class TextAreaForm(ModelForm):
    class Meta:
        model = TextArea
        fields = ["content"]
