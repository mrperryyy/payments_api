from flask import jsonify, make_response
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    response = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown Error')}
    if message:
        response['message'] = message
    
    response = jsonify(response)
    response.status_code = status_code
    return response

def bad_request(error, debug=False):
    if debug:
        print(error)
    if not isinstance(error, str):
        error = str(error)

    return error_response(400, error) 

def successful_response(status_code, payload, location=None):
    response = make_response(jsonify(payload), status_code)
    if location:
        response.headers['Location'] = location
    return response
