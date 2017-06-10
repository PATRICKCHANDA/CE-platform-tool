from flask import Flask, render_template, jsonify, redirect, url_for, request, make_response, g
from services.load_data import DataLoader, create_an_ogrfeature
from services.save_data import DataSaver
from services.ce_analysis import CEAnalysis, traverse_to_upstream_process, prepare_upstream_process

app = Flask(__name__)
factories = {}
all_chemicals = {}
all_reactions = {}
all_utility_info = {}
all_emission_data = {}
analyzer = None


@app.route('/addRftoFactory/<int:rf_id>/<int:factory_id>', methods=['POST'])
def add_a_product_line_to_factory(rf_id, factory_id):
    """
    add a new product line into the factory
    :param factory_id: 
    :param rf_id: new product line id, which is the reaction_formula id 
    :return: 
    """
    global analyzer

    # todo: from client side, post enough information
    content = request.get_json()
    # if 'product_chem_id' not in content:
    #     return jsonify({'error': 'no product_chem_id information'})
    # if 'quantity' not in content:
    #     return jsonify({'error': 'no quantity information'})
    # product_chem_id = content['product_chem_id']
    # product_chem_id_quantity = content['quantity']

    if factory_id not in factories:
        return jsonify({'error': "unknown factory_id " + str(factory_id)})
    if rf_id in factories[factory_id].factory_product_lines:
        return jsonify({"info": "process existed already in the factory."})
    if rf_id not in all_reactions:
        return jsonify({"error": "unknown process in the system."})
    factory = factories[factory_id]
    # todo? those data should be acquired from content

    # create a feature, add the reference chemical first into the productline, this will setup the reference
    # chemical and quantity for this product line
    feature = {"desired_chemical_id": int(content['ref_chemical_id']),
               "desired_quantity": content['ref_chemical_quantity'],
               "unit": 'T',  # the unit of the input quantity is T
               "days_of_production": 340,
               "hours_of_production": 24,
               "inlet_temperature": 20,
               "inlet_pressure": 1,
               "level_reactions": -1,
               "conversion": all_reactions[rf_id].default_conversion,
               "percent_heat_removed": 0.02
               }
    factory.add_product_line(feature, rf_id, all_reactions, all_chemicals)

    # add other products of this product line, should based on user input, currently we add all products
    for chem_id, quantity in content['products'].items():
        feature['desired_chemical_id'] = int(chem_id)
        feature['desired_quantity'] = quantity
        # add the product line, which will add 1 product of this product line(reaction/process)
        factory.add_product_line(feature, rf_id, all_reactions, all_chemicals)

    factory.calculate_byproducts_per_product_line(all_chemicals)
    factory.calculate_emission_per_product_line(all_emission_data)
    factory.calculate_utilities_per_product_line(all_utility_info, all_chemicals)
    print(url_for('get_factory_products', factory_id=factory_id))

    # update the CE_analyzer: add the factory product line info
    analyzer.compare_begin()
    analyzer.process_factory_product_line_info(factory_id, factory.factory_product_lines[rf_id], True)
    quantity_per_compnent = analyzer.calc_total_quantity_per_item()
    # find the upstream process
    new_entries = prepare_upstream_process(all_reactions, analyzer, quantity_per_compnent, rf_id)
    # do calculation
    results = traverse_to_upstream_process(analyzer, new_entries, factories, factory_id, rf_id, all_emission_data,
                                           all_utility_info, all_chemicals, all_reactions)
    if results[0] is False:
        return jsonify(error=results[1])
    else:
        return redirect(url_for("get_factory_products", factory_id=factory_id))


@app.teardown_appcontext
def close_db(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'postgres_db_loader'):
        g.postgres_db_loader.close()
    if hasattr(g, 'postgres_db_saver'):
        g.postgres_db_saver.close()


@app.route('/chemicals')
def edit_chemical_page():
    return render_template("edit_chemical.html")


@app.route('/chemical-processes')
def edit_chemical_process_page():
    return render_template("edit_chemical_process.html")


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
            # print(feature_collection)
            return jsonify(feature_collection)
        else:
            print("factories is NONE.")


@app.route('/getAllReactions')
def get_all_reaction_formula():
    return jsonify([(rf_id, rf.json_format) for rf_id, rf in all_reactions.items()])


@app.route('/getAllChemicals')
def get_all_chemicals():
    return jsonify([(chem_id, chem.json_format) for chem_id, chem in all_chemicals.items()])


@app.route('/getFactoryIds/<int:factory_id>/<string:item_type>/<string:item_name>/<int:as_supplier>', methods=['GET'])
def get_factory_ids_dealing_with_item(factory_id, item_type, item_name, as_supplier):
    """
    based on the item type(emission, utility, chemical), and name(string or id), find all factories which use this
    as their input or supply it as their output
    :param factory_id:
    :param item_type: chemical/emission/utility
    :param item_name: can be an id or name(emission)
    :param as_supplier: indicate this factor supply this item, we need to find factory USE this item, 
    or another way round.
    :return: json format of a list of id's
    """
    global analyzer
    ids = analyzer.get_factory_ids_by_col_id(item_name, item_type[0], not as_supplier)
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
    """
    each product line product a product
    :param factory_id: 
    :return: 
    """
    if factory_id in factories:
        products = factories[factory_id].factory_products_json
        return jsonify(products)
    else:
        print(factory_id, " does not exist.")
        return jsonify("factory does not exist.")


def get_db(need_loader=True):
    """Opens a new database connection if there is none yet for the current application context.
    """
    if need_loader:
        if not hasattr(g, 'postgres_db_loader'):
            g.postgres_db_loader = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
        return g.postgres_db_loader
    else:
        if not hasattr(g, 'postgres_db_saver'):
            g.postgres_db_saver = DataSaver('localhost', 'CE_platform', 'Han', 'Han')
        return g.postgres_db_saver


@app.route("/getTotalRevenue")
def get_whole_area_revenue():
    total_revenue = 0
    unit = ""
    for factory in factories.values():
        total_revenue += factory.factory_revenue[0]
        if factory.factory_revenue[1] != '':
            unit = factory.factory_revenue[1]
    return jsonify(total_revenue, unit)


@app.route("/getDifference")
def get_difference_of_whole_area():
    diff_result = analyzer.compare(all_chemicals, all_utility_info, factories)
    return jsonify(diff_result)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/area-overview')
def overview():
    return render_template("area_overview.html")


"""
functions get the request from the client side
"""


@app.route('/setChemical', methods=['POST'])
def update_chemical():
    """
    update existed chemical or insert new chemical
    :return: 
    """
    content = request.get_json()
    db_saver = get_db(False)  # DataSaver('localhost', 'CE_platform', 'Han', 'Han')
    result = db_saver.update_chemical(content)
    db_saver.close()
    if result[0]:
        return jsonify(msg="编辑化工品成功(update chemical succeed.)")
    else:
        return jsonify(msg=result[1])


@app.route('/setReactionformula', methods=['POST'])
def update_reaction_formula():
    """
    insert new reaction formula
    :return: 
    """
    content = request.get_json()
    db_saver = get_db(False)  # DataSaver('localhost', 'CE_platform', 'Han', 'Han')
    result = db_saver.update_reaction_formula(content)
    if result[0]:
        message = True
    else:
        message = result[1]
    db_saver.close()
    return jsonify(msg=message)


@app.route('/calcFactoryProductLine/<int:factory_id>/<int:rf_id>', methods=['POST'])
def update_factory_product_line(factory_id, rf_id):
    """
    (re)calculate a factory's one product line(process), including the material, byproducts, emissions, utilities
    :param factory_id: 
    :param rf_id: reaction_formula_id
    :return: 
    """
    content = request.get_json()
    if __debug__:
        print(content)
    if factory_id not in factories:
        return jsonify({"error": "unknown factory_id " + str(factory_id)})
    if rf_id not in factories[factory_id].factory_product_lines:
        return jsonify({"error": "unknown reaction_formula_id " + str(rf_id) + " in factory " + str(factory_id)})
    # product_id = content['id']
    # a_productline = factories[factory_id].factory_product_lines[rf_id]

    # get current quantity
    curt_product_id = content['desired_chemical_id']
    curt_quantity = factories[factory_id].factory_product_lines[rf_id].products[curt_product_id].quantity
    # calc and save extra quantity: because if there are factories bond with process, need to UPDATE the total quantity
    content['desired_quantity'] = content['desired_quantity'] - curt_quantity  # >0:increase;  <0: decrease
    new_entry = [{rf_id: ([factory_id], content)}]
    analyzer.compare_begin()
    results = traverse_to_upstream_process(analyzer, new_entry, factories, factory_id, rf_id, all_emission_data,
                                           all_utility_info, all_chemicals, all_reactions)
    if not results[0]:
        return jsonify(msg=results[1])
    return jsonify(msg=results[1])


#-----------------------------------
#-----------------------------------
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
    # initial the __A and __prev_total_margin
    analyzer.compare_begin()
    # analyzer_json = jsonify(analyzer)
    print(analyzer)

if __name__ == '__main__':
    # app_init()
    app.run(host='0.0.0.0', debug=True)
    # host 0.0.0.0 means it is accessiable from any device on the network