from functools import wraps
from flask import request, abort
import sys
import jwt
from api import log

def requires_auth(func):
  @wraps(func)
  def func_wrapper(*args, **kwargs):
    
    # decode the session cookie
    try:
      session_id = request.cookies['session_id']

      # TODO: read secret from configuration
      session_id = jwt.decode(session_id, 'secret', algorithms=['HS256'])
      # TODO: Validate the claims and token expiration
    except:
      log.error('unable to decode session')
      log.error(sys.exc_info()[0])
      abort(401)

    return func(*args, **kwargs)
  return func_wrapper
