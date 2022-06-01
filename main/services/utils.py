import json


def convert_to_model_obj_from_json(data: dict, model_object):
    return model_object.from_json(json.dumps(data))
