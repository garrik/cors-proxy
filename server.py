# -*- coding: utf-8 -*-


import flask
import requests

from flask import make_response


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

    if flask.request.method == 'OPTIONS':
        print(f"Sending fake preflight response to {flask.request.method} {url}")
        return _build_cors_preflight_response()

    print(f"Sending {flask.request.method} {url}")
    # print(f"Sending {flask.request.method} {url} with headers: {flask.request.headers} and data {flask.request.form}")
    r = requests.request(flask.request.method, url, params=flask.request.args, stream=True, headers=flask.request.headers, allow_redirects=False, data=flask.request.form)
    print(f"Got {r.status_code} response from {url}")
    headers = dict(r.raw.headers)
    def generate():
        for chunk in r.raw.stream(decode_content=False):
            yield chunk
    response = flask.Response(generate(), headers=headers)
    response.status_code = r.status_code
    # response.headers['Content-Security-Policy']='default-src \'self\' http://*; connect-src *;'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    # Note that the Authorization header can't be wildcarded and always needs to be listed explicitly.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers
    response.headers.add('Access-Control-Allow-Headers', "Authorization, *")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

if __name__ == '__main__':
    app.debug = True
    app.run()
