#!/usr/bin/env bash


mkdir -p /srv/resume/certs
test -f /etc/letsencrypt/live/srvr.farm/fullchain.pem || cp /etc/letsencrypt/live/srvr.farm/fullchain.pem /srv/resume/certs/
test -f /etc/letsencrypt/live/srvr.farm/privkey.pem || cp /etc/letsencrypt/live/srvr.farm/privkey.pem /srv/resume/certs/

docker network create -d bridge resume-net

docker pull nginx:latest
docker container rm -f mark.srvr.farm 2>/dev/null || true
docker run --rm \
	--net resume-net \
	--name mark.srvr.farm \
	-p 10.0.0.64:8084:80 \
	--volume /srv/resume/html:/usr/share/nginx/html:ro \
	--volume /srv/resume/conf.d:/etc/nginx/conf.d:ro \
	--volume /srv/resume/certs:/etc/nginx/certs:ro \
	nginx:latest ;

