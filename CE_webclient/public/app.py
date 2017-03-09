from flask import Flask, render_template, jsonify, redirect, url_for, request, make_response
from services.load_data import DataLoader

app = Flask(__name__)
db_loader = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
factories = {}

@app.route('/')
def index():
    return render_template("index.html")


# http://stackoverflow.com/questions/32288722/call-python-function-from-js
@app.route('/getFactory', methods=['GET'])
def get_factory():
    if request.method == 'GET':
        if db_loader:
            factories_json_collection = db_loader.get_factories(factories)
            print(factories_json_collection)
            return jsonify(factories_json_collection)
        else:
            print("db_loader is NONE.")


@app.route('/getFactoryProducts/<factory_id>')
def get_factory_products(factory_id):
    if db_loader:
        products = db_loader.get_factory_products(factory_id)
        return jsonify(products)
    else:
        print("db_loader is NONE.")

if __name__ == '__main__':
    # db_loader = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
    app.run(host='0.0.0.0', debug=True)
    # host 0.0.0.0 means it is accessable from any device on the network
