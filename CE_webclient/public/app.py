from flask import Flask, render_template, jsonify, redirect, url_for, request, make_response, g
from services.load_data import DataLoader
from services.ce_analysis import CEAnalysis, SHORT_NAME_FACTORY, SHORT_NAME_EMISSION, \
    SHORT_NAME_UTILITY_TYPE, SHORT_NAME_CHEMICAL

app = Flask(__name__)
factories = {}
all_chemicals = {}
all_reactions = {}
all_utility_info = {}
all_emission_data = {}
analyzer = None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/calcFactoryProductLine/<int:factory_id>/<int:rf_id>', methods=['POST'])
def calc_factory_productline(factory_id, rf_id):
    """
    (re)calculate a factory's one product line, including the material, byproducts, emissions, utilities
    :param factory_id: 
    :param rf_id: reaction_formula_id
    :return: 
    """
    content = request.get_json()
    print(content)
    if factory_id not in factories:
        return jsonify({"error": "unknown factory_id " + str(factory_id)})
    if rf_id not in factories[factory_id].factory_product_lines:
        return jsonify({"error": "unknown reaction_formula_id " + str(rf_id) + " in factory " + str(factory_id)})
    product_id = content['id']
    a_process = factories[factory_id].factory_product_lines[rf_id]
    # update the specific process_line of this factory
    if rf_id in all_emission_data:
        results = a_process.update_process_line(content, product_id, all_utility_info, all_chemicals, all_emission_data[rf_id])
    else:
        results = a_process.update_process_line(content, product_id, all_utility_info, all_chemicals, None)
    if not results[0]:
        return jsonify(msg=results[1])
    return jsonify(msg='succeed processed')


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


@app.route('/getFactoryIds/<int:factory_id>/<string:component_type>/<string:component_name>/<int:as_supplier>', methods=['GET'])
def get_factory_ids_dealing_with_component(factory_id, component_type, component_name, as_supplier):
    """
    :param factory_id:
    :param component_type: chemical/emission/utility
    :param component_name: can be an id or name(emission)
    :param as_supplier: indicate this factor supply this component, we need to find factory USE this component, 
    or another way round.
    :return: 
    """
    global analyzer
    ids = analyzer.get_factory_ids_by_col_id(component_name, component_type[0], not as_supplier)
    # get rid of current factory_id
    return jsonify(ids)


@app.route('/getFactoryProductLine/<int:factory_id>/<int:rf_id>', methods=['GET'])
def get_factory_product_line(factory_id, rf_id):
    """
    :param factory_id: 
    :param rf_id: 
    :return: a specific product line (process) of a specified factory  
    """
    if factory_id in factories and rf_id in factories[factory_id].factory_product_lines:
        a_product = factories[factory_id].factory_product_lines[rf_id].factory_process_json
        return jsonify(a_product)
    else:
        msg = "factory ", factory_id, " or reaction", rf_id, " does not exist."
        print(msg)
        return jsonify(None)


@app.route('/getFactoryProductLines/<int:factory_id>')
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
    global all_utility_info
    global all_emission_data
    global analyzer
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
    # get products, byproducts and emission of all factories
    db_loader.get_factories_products(factories, all_reactions, all_chemicals, all_emission_data)
    # get utilities of all factories
    db_loader.get_factories_utilities(factories, all_utility_info, all_chemicals)
    db_loader.close()

    # construct a analyzer
    analyzer = CEAnalysis(factories, all_chemicals, all_utility_info, all_emission_data)
    # fill in the data
    for factory_id, factory in factories.items():
        for rf_id, product_line in factory.factory_product_lines.items():
            info = product_line.factory_process_json
            # factory products
            for product in info['products']:
                # get product object_id
                analyzer.set_value(factory_id, product['id'], SHORT_NAME_CHEMICAL, product['quantity'])
            # by-products
            for byproduct in info['by_products']:
                analyzer.set_value(factory_id, byproduct['id'], SHORT_NAME_CHEMICAL, byproduct['quantity'])
            # material
            for material in info['material']:
                analyzer.set_value(factory_id, material['id'], SHORT_NAME_CHEMICAL, -material['quantity'])
            # utilities
            # todo: factory may provide utility services,
            for utility in info['utilities']:
                analyzer.set_value(factory_id, utility['id'], SHORT_NAME_UTILITY_TYPE, -utility['quantity'])
            # emissions
            for emission in info['emissions']:
                analyzer.set_value(factory_id, emission['name'], SHORT_NAME_EMISSION, emission['quantity'])
    # analyzer_json = jsonify(analyzer)
    print(analyzer)

if __name__ == '__main__':
    # app_init()
    app.run(host='0.0.0.0', debug=True)
    # host 0.0.0.0 means it is accessable from any device on the network


# todo: added value per unit material
# todo: added value/unit material