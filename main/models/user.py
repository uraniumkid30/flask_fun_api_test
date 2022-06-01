import mongoengine as me


class User(me.Document):
    id = me.StringField(
        primary_key=True,
    )
    first_name = me.StringField()
    last_name = me.StringField()
    email = me.EmailField()
    password = me.StringField()

    def __repr__(self):
        return "<User(name={self.first_name!r})>".format(self=self)
