from db import Store
from urlshort import UrlShorten
import os
import falcon
import json
import configparser
from redis import Redis, exceptions
from urllib.parse import urlunparse, urlparse

config = configparser.ConfigParser()
config.read('config.ini')

try:
    scheme = os.environ["SCHEME"]
    ip_address = os.environ["IP_ADDRESS"]
    port = os.environ["PORT"]
except KeyError:
    scheme = "http"
    ip_address = "localhost"
    port = 80

DB_HOST = config['redis']['host']
DB_PORT = int(config['redis']['port'])
DB_TABLE = int(config['redis']['db_table'])

r = Redis(DB_HOST, DB_PORT, DB_TABLE)
store = Store(r)


class UrlShortener:

    def _create_shorten_url(self, url: str):
        netloc = ip_address
        unique, short_url = UrlShorten.shorten_url(url, scheme, netloc)

        store.keep(short_url, url)
        return short_url

    def _uri_validator(self, url: str):

        try:
            result = urlparse(url)
            if result.path:
                return all([result.scheme, result.netloc, result.path])
            return all([result.scheme, result.netloc])
        except:
            return False

    def on_get(self, req, resp):
        try:
            url = req.get_param("url")
        except Exception:
            resp.media = {"Error": True, "Error Type": "Url param - not found"}
            resp.status = falcon.HTTP_400
            return resp.media, resp.status

        if url:
            if self._uri_validator(url):
                if store.get_count_of_keys() <= 50:
                    response = {"error": False, "shortened_url": self._create_shorten_url(url)}
                    resp.media = response
                    resp.status = falcon.HTTP_200
                    return resp.media, resp.status
                else:
                    response = {"Error": True, "Error type": "No more urls can be added"}
                    resp.media = response
                    resp.status = falcon.HTTP_400
                    return resp.media, resp.status
            else:
                response = {"Error": True, "Error type": "Not valid url"}
                resp.media = response
                resp.status = falcon.HTTP_400
                return resp.media, resp.status


class UrlExpander:
    def on_get(self, req, resp):
        try:
            url = req.get_param("url")
        except Exception:
            resp.media = {"Error": True, "Error Type": "Long url param - not found"}
            resp.status = falcon.HTTP_400
            return resp.media, resp.status
        if url:
            in_db = store.value_of(url)
            if in_db:
                response = {"error": False, "expanded_url": in_db}
                resp.media = response
                resp.status = falcon.HTTP_200
                return resp.media, resp.status
            else:
                response = {"error": True, "expanded_url": "Not presented in db"}
                resp.media = response
                resp.status = falcon.HTTP_400
                return resp.media, resp.status

        if url == "":
            response = {"error": True, "expanded_url": "No url provided to expand"}
            resp.media = response
            resp.status = falcon.HTTP_400
            return resp.media, resp.status


api = falcon.API()

api.add_route('/shorten', UrlShortener())

api.add_route('/expand', UrlExpander())
