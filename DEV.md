heroku logs --tail --app pulse-fi

# Run the app locally
python src/run.py

https://dev.fitbit.com/apps

# if the flask database models have changed, run the following commands, this uses flask-migrate to update the database based on the models in python so the developer does not have to manually update the database in sql
flask db migrate -m 'description of database change'
flask db upgrade