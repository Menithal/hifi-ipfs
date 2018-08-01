from urllib.parse import urlencode, urlparse
import http.client
from http.client import HTTPException


def _http_connect(server):
    if(server.find("https://") != -1):
        return http.client.HTTPSConnection(server.replace("https://", ""))
    else:
        return http.client.HTTPConnection(server.replace("http://", ""))


def oauth_connect(url, oauth, method="GET"):
    
    url = urlparse(url)
    connection = _http_connect(url.netloc)
    data = None

    try:
        connection.connect()
        connection.request(method, url.path, {}, {"Authorization": "Bearer " + oauth})
        res = connection.getresponse()
        data = res.read()

    except HTTPException as e:
        print("HttpException Occurred", e)
        # TODO: Should probably throw Exception here.
        return None
    finally:
        connection.close()

    return data.decode("utf-8")
