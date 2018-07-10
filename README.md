# Hifi-IFPS "Heimdall"
## Web Node Proof of Concept

This is a proof of concept repository for rapidly setting up a service that allows one to upload content to IPFS network that then can be used within High Fidelity. 

Others may use this as a base line to make their own host nodes for ipfs with their own services.

# Requirements

- Docker
- Docker Compose

# Structure

- `app` folder contains the source of the Basic Python Flask web service that is used to interface with ipfs
- `Dockerfile` contains the Docker build file to build the python Flask webservice.
- `docker-compose.yml` contains the docker compose file to run the entire service stack. This includes:
   - gatekeeper - Built in this repository. Filters content that goes to the ipfs and gives a barebones ui to track what has been sent to it.
   - ipfs - Interplanetary File System Node https://github.com/ipfs/go-ipfs
   - db - Simple Credentials access control and Keeping track of file hashes, as a PSQL db example

The repository of it self contains both the python files for the prototype web service, and the docker compose file to start the entire service.

### To run

To run the service

```
docker-compose build;
docker-compose pull;
docker-compose up;
```
This builds the current state of the service, and starts the entire stack using docker compose.

Once built, you no longer need build the service again.
Simply running `docker-compose up` will get the entire service up and running.

If developing and you wish to rebuild the gatekeeper, use the  
```
source rebuild.sh
```
Shortcut to build the python service.

### Basics Docker-Compose
- `docker-compose build` - build anything that needs building.
- `docker-compose pull` - grabs all the latest versions of the files
- `docker-compose up -d` - puts all the services online, detachhed
- `docker-compose down` - shut down all the services


# Dev Requirements

To continue developing the project on your own or in your own fork, make sure to install the pip packages

The Current dev setup uses
```
pip install Flask==1.0.2 ipfsapi==0.4.3 flask_sqlalchemy==2.3.2 flask-marshmallow==0.9.0 Flask-Migrate==2.2.1 psycopg2-binary==2.7.5 python-dotenv==0.8.2
``` 
Feel free to update versions as they get update, and if you do, submit a pull request.


### Gatekeeper Routes
- `/plugin_routes` - Gives an overview of available routes for any plugin to use. This should always be available, as plugins will use this as references
- `/new` 
    - *GET* - Interface for generating pseudoanonymous tokens that behave as username - token pairs
    - *POST* - Generates a unique token for username, returns it in JSON
- `/uploads` - Login to check all the IPFS files uploaded on this username - token combo.
    - *GET* - Interface for generating
    - *POST* - Lists all IPFS links uploaded with username - token pair, returned as JSON
- `/upload` 
    - *GET* - Interface to push zip / fbx files with. Needs username and token.
    - *POST* - multipart/form-data, where "file" should be a zip file, and username token should be defined

### Plugins and /plugin_routes 

`/plugin_routes` This allows the service to be developed in other languages as well, if one so wishes, using their own route conventions. The routes is the first thing loaded by a Modelling package plugin (MPP), such as the Blender Plugin. This should return a json map with the following keys: 

- `new_user` - should point to an interface where the user can generate a new identity. The MMP should simply open the browser for the end user and point it to this url. 
- `asset_upload` - Should point to a POST interface which allows MMPs to POST a multipart/form-data file, with a username and token
- `uploads` - Should point to an interface where the user can check all the links generated under their account that point to the ipfs and manage it there.

# License 

See LICENSE.md