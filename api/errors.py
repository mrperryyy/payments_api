from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    response = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown Error')}
    if message:
        response['message'] = message
    
    response = jsonify(response)
    response.status_code = status_code
    return response

def bad_request(message):
    return error_response(400, message)