# artivatic_ai

Send Email and create logs using ELK Stack

Intall ELK Stack

Using: `https://logz.io/blog/elk-mac/`

Using Pipenv run step to setup:
Install Pipenv: `brew install pipenv`

Setup App:
Copy env file: `cp env\local.txt .env`
To activate virtual env: `pipenv shell`
To Install requirement: `pipenv install -d`

If not using Pipenv:-
Install Requirement: `pip install -r requirements.txt`

Than Run LogStash:
`path/bin/logstash -f logstash.conf`

Run ELK:

Elasticsearch: `http://localhost:9200`
Logstash: `http://localhost:9600`
Kibana: `http://localhost:5601`
