from flask import Flask, render_template, jsonify, redirect, url_for, request, make_response, g
from services.load_data import DataLoader, create_an_ogrfeature
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


@app.route('/addRftoFactory/<int:rf_id>/<int:factory_id>')
def add_a_productline_to_factory(rf_id, factory_id):
    """
    add a new product line into the factory
    :param factory_id: 
    :param rf_id: new product line id, which is the reaction_formula id 
    :return: 
    """
    global analyzer
    if factory_id not in factories:
        return jsonify({'error': "unknown factory_id " + str(factory_id)})
    if rf_id in factories[factory_id].factory_product_lines:
        return jsonify({"info": "process existed already in the factory."})
    if rf_id not in all_reactions:
        return jsonify({"error": "unknown process in the system."})
    factory = factories[factory_id]
    # create a feature
    # todo: those data should be acquired via Database after user has add a process information into a factory
    # todo: currently we create a feature
    # db_loader = get_db()
    # db_loader.get_factory_product(factory_id, rf_id)
    # db_loader.close()
    field_names = ["desired_chemical_id", "desired_quantity", ("unit", 1), "days_of_production", "hours_of_production",
     "inlet_temperature", "inlet_pressure", "level_reactions", "conversion", "percent_heat_removed"]
    field_types = ["I", "I", "S", "I", "I", "F", "F", "I", "F", "F"]
    # if there are more than 1 products in this process, choose the one whose quantity is 1
    product_chem_id = next(iter(all_reactions[rf_id].products.keys()))
    values = [product_chem_id, 45199, 'T', 340, 24, 20, 1, -1, 0.7, 0.02]
    # todo: add other products of this productline, should based on user input, currently we add all products
    for chem_id, detail in all_reactions[rf_id].products.items():
        values[0] = chem_id
        feature = create_an_ogrfeature(field_names, field_types, values)
        # add the product line, which will add 1 product of this product line
        factory.add_product_line(feature, rf_id, all_reactions, all_chemicals)

    factory.calculate_byproducts_per_product_line(all_chemicals)
    factory.calculate_emission_per_product_line(all_emission_data)
    factory.calculate_utilities_per_product_line(all_utility_info, all_chemicals)
    print(url_for('get_factory_products', factory_id=factory_id))
    # update the CE_analyzer: add the factory product line info
    analyzer.process_factory_product_line_info(factory_id, factory.factory_product_lines[rf_id], True)
    return redirect(url_for("get_factory_products", factory_id=factory_id))


@app.route('/calcFactoryProductLine/<int:factory_id>/<int:rf_id>', methods=['POST'])
def update_factory_productline(factory_id, rf_id):
    """
    (re)calculate a factory's one product line(process), including the material, byproducts, emissions, utilities
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
    a_productline = factories[factory_id].factory_product_lines[rf_id]

    # 1. update the CE_analyzer: minus the info from the CE_analyzer
    analyzer.process_factory_product_line_info(factory_id, a_productline, False)

    # 2. update the specific product_line of this factory
    if rf_id in all_emission_data:
        results = a_productline.update_process_line(content, product_id, all_utility_info, all_chemicals, all_emission_data[rf_id])
    else:
        results = a_productline.update_process_line(content, product_id, all_utility_info, all_chemicals, None)

    # 3. update the CE_analyzer: ADD the info into the CE_analyzer
    analyzer.process_factory_product_line_info(factory_id, a_productline, True)
    if not results[0]:
        return jsonify(msg=results[1])
    return jsonify(msg='succeed processed')


# http://stackoverflow.com/questions/32288722/call-python-function-from-js
@app.route('/getFactory', methods=['GET'])
def get_factory():
    """
    :return: json format of all factory basic information 
    """
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
    based on the component type(emission, utility, chemical), and name(string or id), find all factories which use this
    as their input or supply it as their output
    :param factory_id:
    :param component_type: chemical/emission/utility
    :param component_name: can be an id or name(emission)
    :param as_supplier: indicate this factor supply this component, we need to find factory USE this component, 
    or another way round.
    :return: json format of a list of id's
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


@app.route("/getTotalRevenue")
def get_whole_are_revenue():
    total_revenue = 0
    unit = ""
    for factory in factories.values():
        total_revenue += factory.factory_revenue[0]
        if factory.factory_revenue[1] != '':
            unit = factory.factory_revenue[1]
    return jsonify(total_revenue, unit)


@app.teardown_appcontext
def close_db(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'postgres_db'):
        g.postgres_db.close()


def app_init():
    """
    server initialization
    """
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
    analyzer.process_all_factories_information(factories)

    # analyzer_json = jsonify(analyzer)
    print(analyzer)

if __name__ == '__main__':
    # app_init()
    app.run(host='0.0.0.0', debug=True)
    # host 0.0.0.0 means it is accessiable from any device on the network