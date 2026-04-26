# ClickGuard API

### Running API
In order to run the app:
- install python > 3.11
- specify OPEN_API_KEY in `.env` file
- install requirements by running <br>
`pip install -r requirements.txt`
- to start the service run <br>
`python main.py`
- service will be running on localhost:8080

### Running tests

In order to run tests, in the main folder run: <br>
`PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py"`