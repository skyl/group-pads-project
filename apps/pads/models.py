import django
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.template.defaultfilters import slugify

class Pad(models.Model):
    """The room where collaborative editing and chat happens

    """

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    group = generic.GenericForeignKey("content_type", "object_id")
    guid = models.CharField(max_length=32, unique=True) #md5 hash of `title.lower()`
    title = models.CharField( max_length=255 )
    slug = models.CharField( max_length=255 )
    creator = models.ForeignKey(User, related_name="pads_owned" ) #User who created Pad
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ( ( 'slug', 'creator'), ('title', 'creator') )
        ordering = ('modified', )

    def __unicode__(self):
        return '({user}) -- {title}'.format(
            user=self.creator,
            title=self.title,
        )

    @models.permalink
    def get_absolute_url(self):
        return ( 'pads_detail', (), { 'creator': self.creator.username, 'slug': self.slug,  } )

    def save(self):
        self.slug = slugify( self.title )

        # catch non-unique slugs in the form before it comes to this
        # this is like the 'you made a dupe on yourself, now you get a
        # nonsense slug' nonanswer.
        if Pad.objects.filter( creator=self.creator, slug=self.slug ):
            from random import shuffle
            l = list(self.slug)
            shuffle(l)
            self.slug = ''.join(l)
        super(Pad, self).save()

    def delete(self):
        """Delete all associated Revisions

        """

        TextAreaRevision.objects.filter(
                pad_guid=self.pad.guid
        ).delete()

        super(Pad, self).delete()


class TextArea(models.Model):
    """Pad objects can have multiple TextArea objects keyed to them

    """

    pad = models.ForeignKey(Pad)
    content = models.TextField( blank=True )
    editor = models.ForeignKey(User) #User who edited Pad
    edit_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-edit_time',)

    def __unicode__(self):
        return '{pad} - {content}'.format(
            pad=self.pad,
            content=self.content[:20],
        )

    ''' This can't be the thing to do
    def save(self, *args, **kwargs):
        """Save a Revisioned copy after the real save.
        """
        super(TextArea, self).save(*args, **kwargs)
        new_revision = TextAreaRevision()
        new_revision.pad_guid=self.pad.guid
        new_revision.content=self.content
        new_revision.editor=self.editor
        new_revision.edit_time=self.edit_time
        new_revision.save()
    '''

class TextAreaRevision(models.Model):
    """Snapshot of the current TextArea state
    """
    pad_guid = models.CharField(max_length=32)
    content = models.TextField( blank=True )
    editor = models.ForeignKey(User) #User who edited Pad
    edit_time = models.DateTimeField( auto_now_add=True )

    class Meta:
        ordering = ("-edit_time",)

    def __unicode__(self):
        return '{editor} - {time} - {content}'.format(
            editor=self.editor,
            time=self.edit_time,
            content=self.content[:50],
        )

