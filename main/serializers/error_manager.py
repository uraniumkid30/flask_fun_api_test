from marshmallow import Schema
from utilities.utils import Status


def validate_fields(request_payload: dict, schema: Schema):
    try:
        schema.load(request_payload).data
    except Exception as err:
        # print(type(err.data))
        # print(type(err.messages))
        return {
            "errors": err.messages,
            "message": f"Remove Unnecessary fields {list(err.messages.keys())}",
        }, Status.HTTP_400_BAD_REQUEST
    else:
        return True
