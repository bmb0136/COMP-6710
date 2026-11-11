import sys
from flask import Flask, request, jsonify

def create_app():
    app = Flask(__name__)

    @app.route('/ssp', methods=['GET'])
    def ssp():
        return "Secure Software Process"

    @app.route('/vanity', methods=['GET'])
    def vanity():
        return "Brandon Buckley"

    @app.route('/mypython', methods=['GET'])
    def mypython():
        return sys.version

    @app.route('/csse', methods=['GET'])
    def csse():
        return "Department of Computer Science and Software Engineering"

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
