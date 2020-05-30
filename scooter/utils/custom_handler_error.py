from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is not None:
        data = response.data
        response.data = {}
        errors = []
        try:
            for field, value in data.items():
                error_dict = dict()
                error_dict['field'] = str(field)
                # When you get more value errors
                if isinstance(value, type([])):
                    for val in value:
                        if val:
                            value = val
                            break
                        continue
                # When serializer validators are nested
                if isinstance(value, type({})):
                    value = value.get('non_field_errors', value)
                    if isinstance(value, type([])):
                        value = value[0]

                    error_dict['message'] = value

                    if not isinstance(value, type({})):
                        error_dict['code'] = value.code

                    errors.append(error_dict)

                # If value is not list
                else:
                    error_dict['message'] = value
                    if not isinstance(value, type({})):
                        error_dict['code'] = value.code
                    errors.append(error_dict)

        except Exception as ex:
            print("Exception in custom handler error, please check it")
            print(ex.args.__str__())
            return {'errors': {"field": "detail", "message": "Error desconocido"}, "status": False}
        response.data['errors'] = errors[0]
        response.data['status'] = False

        # response.data['exception'] = str(exc)
    return response
