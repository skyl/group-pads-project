import unittest
from django.contrib.auth.models import User
from django.db import IntegrityError
from pads.models import TextArea, Pad, TextAreaRevision
from pads.utility import create_pad_guid

class PadCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user1", "user1@example.com", password="password1")
        self.user.save()
        self.second_user = User.objects.create_user("user2", "user2@example.com", password="password2")
        self.second_user.save()

        self._question = "Is Foo the new Bar?"
        self._guid = create_pad_guid(self._question)
        self._content = "No, Foo will always be tops!"

        self.pad = Pad(guid=self._guid, creator=self.user, question=self._question)
        self.pad.save()

        self.textarea = TextArea(pad=self.pad, content=self._content, editor=self.user)
        self.textarea.save()

    def tearDown(self):
        User.objects.all().delete()

    def test_GetPad(self):
        testslug = "is-foo-the-new-bar"
        testguid = create_pad_guid(testslug)
        pad = Pad.objects.get(guid=testguid)
        textarea = pad.textarea_set.get(editor=self.user)
        self.assertEquals(self._question, pad.question)
        self.assertEquals(self.user, pad.creator)
        self.assertEquals(self._content, textarea.content)

    def test_AddNewTextAreabyNewUser(self):
        getpad = Pad.objects.get(guid=self._guid)
        new_textarea = TextArea(pad=getpad, editor=self.second_user, content="Bar will rise and defeat Foo!")
        new_textarea.save()

    def test_editTextArea(self):
        textarea = TextArea.objects.get(pad__guid=self._guid )
        textarea.content = "Foo is best eva."
        textarea.save()
        revs = TextAreaRevision.objects.all()
        self.assertEquals(len(revs), 2)
        self.assertEquals(revs[0].content, textarea.content)
        self.assertEquals(revs[1].content, self._content)
