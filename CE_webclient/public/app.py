from flask import Flask, render_template, jsonify, redirect, url_for, request, make_response, g
from services.load_data import DataLoader
from services.ce_analysis import create_2D_array

app = Flask(__name__)
factories = {}
all_chemicals = {}
all_reactions = {}

@app.route('/')
def index():
    return render_template("index.html")


# http://stackoverflow.com/questions/32288722/call-python-function-from-js
@app.route('/getFactory', methods=['GET'])
def get_factory():
    app_init()
    # global factories
    if request.method == 'GET':
        if factories is not None:
            feature_collection = {"type": "FeatureCollection", "features": []}
            for v in factories.values():
                feature_collection["features"].append(v.factory_basic_info_json)
            print(feature_collection)
            return jsonify(feature_collection)
        else:
            print("factories is NONE.")


@app.route('/getAllReactions')
def get_all_reaction_formula():
    return jsonify([(rf_id, rf.json_format) for rf_id, rf in all_reactions.items()])


@app.route('/getAllChemicals')
def get_all_chemicals():
    return jsonify([(chem_id, chem.json_format) for chem_id, chem in all_chemicals.items()])


@app.route('/getFactoryProducts/<int:factory_id>')
def get_factory_products(factory_id):
    if factory_id in factories:
        products = factories[factory_id].factory_products_json
        return jsonify(products)
    else:
        print(factory_id, " does not exist.")
        return jsonify("factory does not exist.")


def get_db():
    """Opens a new database connection if there is none yet for the current application context.
    """
    if not hasattr(g, 'postgres_db'):
        g.postgres_db = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
    return g.postgres_db


@app.teardown_appcontext
def close_db(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'postgres_db'):
        g.postgres_db.close()


def app_init():
    global factories
    global all_reactions
    global all_chemicals
    db_loader = get_db()    # DataLoader('localhost', 'CE_platform', 'Han', 'Han')
    all_chemicals = db_loader.get_all_chemicals()
    print("[Info]: reading public chemicals...ready")
    all_reactions = db_loader.get_all_reaction_formulas()
    print("[Info]: reading public reaction_formula's...ready")
    all_utility_info = db_loader.get_utility_type()
    print("[Info]: reading gaolanport utility_type...ready")
    all_emission_data = db_loader.get_emission_data()
    print("[Info]: reading public emission data...ready")

    # get factories
    factories = db_loader.get_factories()

    # construct a 2D array
    create_2D_array(factories, all_chemicals, all_utility_info, all_emission_data)

    # get products, byproducts and emission of all factories
    db_loader.get_factories_products(factories, all_reactions, all_chemicals, all_emission_data)
    # get utilities of all factories
    db_loader.get_factories_utilities(factories, all_utility_info, all_chemicals)
    db_loader.close()

if __name__ == '__main__':
    # app_init()
    app.run(host='0.0.0.0', debug=True)
    # host 0.0.0.0 means it is accessable from any device on the network


# todo: added value per unit material
# todo: added value/unit material