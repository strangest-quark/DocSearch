# DocSearch

Site - http://searchecy.netlify.com/

Frontend - https://github.com/ikram-shah/searchECY-Frontend

## Run

The following command builds code changes in /app and brings up app-server, elastic-search and mysql. Server can be tested using hitting endpoints in postman collection.

`sh start.sh`

To bring down existing containers and start fresh use:

`sh restart.sh`

## Postman
https://github.com/strangest-quark/DocSearch/blob/master/Search.postman_collection.json

## Code changes

To be done in /app folder

## Nginx setup

Nginx setup has ssl certs mounting also invloved. To be used only for hosting purposes. This app uses Letsencrypt for generating certs.
