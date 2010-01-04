import django
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.db import IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from pads.models import Pad, TextArea
from pads.forms import PadForm, TextAreaForm
from pads.utility import create_pad_guid

from datetime import datetime
from hashlib import md5

def index(request):
    '''user_pads, recent_pads sent to 'pads/index.html'

    '''

    users_pads = Pad.objects.filter( creator=request.user )
    recent_pads = Pad.objects.all()

    return object_list( request,
        queryset = Pad.objects.all(),
        paginate_by = 50,
        template_name = 'pads/index.html',
        extra_context = locals(),
    )

@login_required
def detail(request, creator=None, slug=None, guid=None):
    '''The Pad object_detail

    '''
    #TODO: check if user is logged in, then enable chat, etc.

    if not guid:
        guid = create_pad_guid(slug)

    try:
        pad = Pad.objects.get(guid=guid)

    except Pad.DoesNotExist:
        raise Http404

    #TODO: I want to enable multiple pads eventually.
    textareas = TextArea.objects.filter(pad=pad)

    if not textareas:
        textarea_a = TextArea( pad=pad, content="", editor=request.user )
        textarea_a.save()

    else:
        textarea_a = textareas[0]

    #TODO: too tightly coupled to contrib.auth, clumsy ...
    if request.user == User.objects.get(username=creator):
        user_is_creator = True
    else:
        user_is_creator = False

    args = {"textarea_a":textarea_a, "user":request.user,
            'textareas': textareas,
            "STOMP_PORT":settings.STOMP_PORT, "CHANNEL_NAME": guid,
            "HOST":settings.INTERFACE, "SESSION_COOKIE_NAME": settings.SESSION_COOKIE_NAME,
            "user_is_creator":user_is_creator,
            }

    return object_detail( request,
            queryset = Pad.objects.all(),
            object_id = pad.id,
            template_object_name = 'pad',
            template_name = 'pads/pad.html',
            extra_context = args,
    )


@login_required
def new(request):
    """
    Create a new Pad, with 1 initial "TextArea" for
    a given choice.

    """
    if request.method == 'POST':
        pad_form = PadForm(request.POST)

        if pad_form.is_valid():
            pad_inst = pad_form.save(commit=False)
            title = pad_form.cleaned_data["title"]

            # TODO is there a reason that this is not factored out to the
            # forms.py?

            pad_inst.creator = request.user
            pad_inst.guid = create_pad_guid(title)
            pad_inst.save()

            textarea_inst = TextArea(pad=pad_inst, editor=request.user )
            textarea_inst.save()
            return HttpResponseRedirect( pad_inst.get_absolute_url() ) # Redirect after POST

    else:
        pad_form = PadForm()

    args = {"pad_form":pad_form, "user":request.user}

    return create_object( request,
            form_class = PadForm,
            template_name = 'pads/new.html',
            extra_context = args,
            #login_required = True,
    )

def add(request, app_label, model_name, id):
    '''Add a pad to another object'''
    try:
        typ = ContentType.objects.get(app_label=app_label, model=model_name)
        obj = typ.get_object_for_this_type(id=id)
    except:
        return HttpResponseNotFound()
    if request.method == 'POST':
        pad_form = PadForm(request.POST)
        if pad_form.is_valid():
            pad_inst = pad_form.save(commit=False)
            pad_inst.creator = request.user
            title = pad_form.cleaned_data["title"]
            pad_inst.guid = create_pad_guid(title)
            pad_inst.content_type = typ
            pad_inst.object_id = id
            pad_inst.save()
            textarea_inst = TextArea(pad=pad_inst, editor=request.user )
            textarea_inst.save()
            return HttpResponseRedirect( pad_inst.get_absolute_url() )
    else:
        pad_form = PadForm()

    return create_object( request,
            form_class = PadForm,
            template_name = 'pads/new.html',
            extra_context = locals(),
    )
