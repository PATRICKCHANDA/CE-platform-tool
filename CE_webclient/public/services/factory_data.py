class FactoryProduct:
    def __init__(self, product_info):
        self.chem_product_name = product_info.GetField('name_en')
        self.reaction_formula_id = product_info.GetField('reaction_formula_id')
        self.quantity = product_info.GetField('desired_quantity')
        self.quantity_unit = product_info.GetField('unit')
        self.__days_of_production = product_info.GetField('days_of_production')
        self.__hours_of_production = product_info.GetField('hours_of_production')
        self.inlet_temperature = product_info.GetField('inlet_temperature')
        self.inlet_pressure = product_info.GetField('inlet_pressure')
        self.level_reactions = product_info.GetField('level_reactions')
        self.value_product = 0
        self.reactants = {}

    @property
    def product_time(self):
        return self.__days_of_production * self.__hours_of_production * 3600  # in seconds


class Factory:
    def __init__(self, info):
        self.__id = info["id"]
        self.__name = info['properties']['name']
        self.__category = info['properties']['category']
        self.__products = {}

    def add_product(self, product_info):
        product_id = product_info.GetField('desired_chemical_id')
        self.__products[product_id] = FactoryProduct(product_info)

    @property
    def factory_id(self):
        return self.__id

    @property
    def factory_name(self):
        return self.__name


