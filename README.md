# artivatic_ai

Send Email and create logs using ELK Stack

Intall ELK Stack

Using: `https://logz.io/blog/elk-mac/`

Using Pipenv run step to setup:
<br>Install Pipenv: `brew install pipenv`

Setup App:

Copy env file: `cp env\local.txt .env`
<br>To activate virtual env: `pipenv shell`
<br>To Install requirement: `pipenv install -d`

If not using Pipenv:-
<br>Install Requirement: `pip install -r requirements.txt`

Than Run LogStash:
<br>`path/bin/logstash -f logstash.conf`

Run ELK:

Elasticsearch: `http://localhost:9200`
<br>Logstash: `http://localhost:9600`
<br>Kibana: `http://localhost:5601`
