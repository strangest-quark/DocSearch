# DocSearch

## Run

The following command builds code changes in /app and brings up app-server, elastic-search and mysql. Server can be tested using hitting endpoints in postman collection.

`sh start.sh`

To bring down existing containers and start fresh use:

`sh restart.sh`

## Postman
https://www.getpostman.com/collections/496c19914859c412f7ad

## Code changes

To be done in /app folder

## Nginx setup

Nginx setup has ssl certs mounting also invloved. To be used only for hosting purposes. This app uses Letsencrypt for generating certs.
