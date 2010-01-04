"""
Handlers that inspect, log, and modify
in-transit Orbited messages.

This file is very application specific,
so there needs to be a clear way to:

    1. Create custom message handlers
    2. Overide of message handlers
    3. "Plug in" custom message handlers


"""
import os
import sys
# Environment setup for your Django project files:
sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.contrib.auth.models import User
from pads.models import Pad, TextArea, TextAreaRevision

try:
    # 2.6 will have a json module in the stdlib
    import json
except ImportError:
    try:
        # simplejson is the thing from which json was derived anyway...
        import simplejson as json
    except ImportError:
        print "No suitable json library found, see INSTALL.txt"

# TODO
# take all below functions and put into an base class and subclass:
# Make 'logging' of all message tunable
# Have base-class use  'getattr' in combination with 'msgtype'.
# to get the appropiate message handler.
def handle_send(msg, username, channel_id):
    msg = json.loads(msg)
    msg.update({"from":username})
    msgtype = msg.get("type")

    if msgtype is None:
        update = {"error":"Missing message type"}

    if msgtype == "chat":
        update = {"from":username}

    if msgtype == "edit":
        content = msg.get("content")
        update = _handle_edit(content, username, channel_id)

    if msgtype == "save":
        content = msg.get("content")
        update = _handle_save(content, username, channel_id)

    #update the message with type specific response info:
    msg.update(update)
    return msg


def _handle_edit(content, username, channel_id):
    """Handle the edit of a Pad's TextArea by a User.

    TODO: Use more efficient diff algorithms/storage.
    """
    textarea = TextArea.objects.get( pad__guid=channel_id )

    if textarea is None:
        return {"error":"No such textarea"}
    user = User.objects.get(username=username)

    if user is None:
        return {"error":"No such user"}
    textarea.content = content
    textarea.editor = user
    textarea.save()

    return {"content":content}

def _handle_save(content, username, channel_id):
    """Just can't see saving on each keystroke.

    Maybe we can run save every so often.
    """

    r = _handle_edit(content, username, channel_id)
    # Do this here instead of each time the TextArea is changed.
    new_revision = TextAreaRevision()
    new_revision.pad_guid = channel_id
    new_revision.content = content
    new_revision.editor = User.objects.get(username=username)
    new_revision.save()

    return r

def handle_subscribe(msg, username, channel_id):
    print "=handle_subscribe= ", msg, username, channel_id
    return msg

def handle_connect(msg, username, channel_id):
    print "=handle_connect= ", msg, username, channel_id
    return msg

def handle_disconnect(msg, username, channel_id):
    print "=handle_disconnect= ", msg, username, channel_id
    return msg


MESSAGE_HANDLERS = {
    "send":handle_send,
    "subscribe":handle_subscribe,
    "connect":handle_connect,
    "disconnect":handle_disconnect
}
