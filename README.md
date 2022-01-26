# urlshortener
srvc on falcon to short or expand urls, via redis

Need Redis,Falcon

Test service run via: gunicorn app:api -b 0.0.0.0:8000

And aviable on http://localhost:8000

API :
/shorten?url={url}
/expand?url={shortened_url}

LIMIT OF MAX URLS IN DB == 50
