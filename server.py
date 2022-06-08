# -*- coding: utf-8 -*-


import flask
import requests

app = flask.Flask(__name__)

method_requests_mapping = {
    'GET': requests.get,
    'HEAD': requests.head,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'PATCH': requests.patch,
    'OPTIONS': requests.options,
}


@app.route('/<path:url>', methods=method_requests_mapping.keys())
def proxy(url):
    print(f'url {url}')
    print(f'flask.request.method {flask.request.method}')

    if flask.request.method == 'OPTIONS':
        print(f'rewrite response')
        from requests.models import Response

        the_response = Response()
#        the_response.code = "expired"
#        the_response.error_type = "expired"
#        the_response.status_code = 400
        the_response.headers['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with'
        the_response.headers['Access-Control-Allow-Methods'] = 'OPTIONS'
        the_response.headers['Access-Control-Allow-Origin'] = '*'
        the_response.headers['Access-Control-Max-Age'] = '86400'
        the_response.headers['Cache-control'] = 'private'
        the_response.headers['Connection'] = 'close'
        the_response.headers['Content-Encoding'] = 'gzip'
        the_response.headers['Content-Length'] = '20'
        the_response.headers['Content-Type'] = 'text/html; charset=utf-8'
        the_response.headers['Date'] = 'Wed, 08 Jun 2022 22:15:40 GMT'
        the_response.headers['Server'] = 'Flask'
        the_response.headers['Set-Cookie'] = 'LB_X_COOKIE_PER=sLLnx2; path=/'
        the_response.headers['Vary'] = 'Origin,Accept-Encoding'
        the_response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        return ('', 200, the_response.headers.items())

    requests_function = method_requests_mapping[flask.request.method]
    request = requests_function(url, stream=True, params=flask.request.args)
    response = flask.Response(flask.stream_with_context(request.iter_content()),
                              content_type=request.headers['content-type'],
                              status=request.status_code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.debug = True
    app.run()
