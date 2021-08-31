from flask import Flask, request
from dailyquote import Qotd

app = Flask(__name__)
qotd = Qotd()

@app.route("/qotd", methods = ['GET'])
def quote_of_the_day():
    if request.method == 'GET':
        return str(qotd), 200
    else:
        return "No service", 401

if __name__ == "__main__":
    app.run()