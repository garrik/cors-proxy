# -*- coding: utf-8 -*-
"""
Setup a proxy to allow debugging of api not accessible because of cors and/or residing in inaccessible network
"""


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

# enable cors proxy features via custom headers
X_HEADER_PROXIES = "X-cp-proxies" # proxies used when forwarding request
X_HEADER_FAKE_PREFLIGHT = "X-cp-fake-preflight" # send a fake preflight response to OPTIONS requests

@app.route('/<path:url>', methods=method_requests_mapping.keys())
def proxy(url):

    if _is_fake_preflight(flask.request) and flask.request.method == 'OPTIONS':
        print(f"Sending fake preflight response to {flask.request.method} {url}")
        return _build_cors_preflight_response()

    proxies = _build_proxies(flask.request)

    print(f"Sending {flask.request.method} {url}")
    # print(f"Sending {flask.request.method} {url} with headers: {flask.request.headers} and data {flask.request.form}")
    r = requests.request(flask.request.method, url, params=flask.request.args, stream=True, headers=flask.request.headers, allow_redirects=False, data=flask.request.form, proxies=proxies)
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

def _is_fake_preflight(request):
    return request.headers.get(X_HEADER_FAKE_PREFLIGHT) == None

# https://stackoverflow.com/questions/12601316/how-to-make-python-requests-work-via-socks-proxy
def _build_proxies(request):
    proxies = {}
    proxies_string = request.headers.get(X_HEADER_PROXIES)
    if proxies_string == None or len(proxies_string) == 0:
        return None
    proxies_pairs=proxies_string.split(',')
    for pair in proxies_pairs:
        proxy_pair = pair.split('=')
        if len(proxy_pair) != 2:
            print('failed to parse proxies')
            return None
        proxies[proxy_pair[0]] = proxy_pair[1]
    return proxies

if __name__ == '__main__':
    app.debug = True
    app.run()
