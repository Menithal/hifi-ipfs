# Hifi-IFPS 
## Web Node Proof of Concept

This is a proof of concept repository for setting up a service that allows on to upload content to IPFS network that then can be used in High Fidelity. Others may use this as a base line to make their own host nodes for ipfs with their own services.

# Requirements

- Docker
- Docker Compose

# Dev Requirements

To continue developing the project on your own or in your own fork, make sure to install the pip packages

The Current setup is
```
pip install Flask==1.0.2 ipfsapi==0.4.3 flask_sqlalchemy==2.3.2 flask-marshmallow==0.9.0 Flask-Migrate==2.2.1 psycopg2-binary==2.7.5 python-dotenv==0.8.2
``` 

Feel free to update, and if you do please update upstream.


# Structure

- `app` folder contains the source of the prototype Python Flask web service that is used to interface with ipfs
- `Dockerfile` contains the Docker build file to build the python Flask webservice.
- `docker-compose.yml` contains the docker compose file to run the entire service stack. This includes:
   - ipfs - Interplanetary File System Node
   - This service, built in this repository.
   - psql - As a Sample for Credentials access control and Keeping track of file hashes, as a db example (this should be migrated elsewhere)

The repository of it self contains both the python files for the prototype web service, and the docker compose file to start the entire service.

The Service it self is available as a Docker image at menithal/hifi-ipfs

# To run

A Bash and Powershell Script are made to allow for developing straight from the repository easier.

```
# Bash
./rebuild.sh
# PS
./rebuild.ps1
```

This builds and starts the entire stack using docker compose.

Once build and running `docker-compose` can be used to maintain the service states.

### Basics 

- `docker-compose pull` - grabs all the latest versions of the files
- `docker-compose up -d` - puts all the services online
- `docker-compose down` - puts all the services down

# License 

See LICENSE.md