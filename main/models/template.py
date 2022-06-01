import mongoengine as me


class Template(me.Document):
    _id = me.StringField(
        primary_key=True,
    )
    template_name = me.StringField()
    subject = me.StringField()
    body = me.StringField()

    def __repr__(self):
        return "<Template(name={self.template_name!r})>".format(self=self)
