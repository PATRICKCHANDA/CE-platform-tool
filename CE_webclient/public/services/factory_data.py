from .unit_conversion import UnitConversion


class FactoryMaterial:
    """
    a factory material
    """
    def __init__(self, name, quantity, value):
        if __debug__:
            self.__name = name
        self.quantity = quantity
        self.value = value  # < 0 means cost of buy, > 0 means product


class FactoryProduct:
    def __init__(self, product_chem_id, product_info):
        """
        initial the factory product and its reactant
        :param product_info: OGRFeature
        """
        self.__product_chem_id = product_chem_id
        self.__chem_product_name = product_info.GetField('name_en')
        self.__chem_product_name_cn = product_info.GetField('name_cn')
        self.__reaction_formula_id = product_info.GetField('reaction_formula_id')
        self.quantity = product_info.GetField('desired_quantity')
        self.quantity_unit = product_info.GetField('unit')
        self.days_of_production = product_info.GetField('days_of_production')
        self.hours_of_production = product_info.GetField('hours_of_production')
        self.inlet_temperature = product_info.GetField('inlet_temperature')
        self.inlet_pressure = product_info.GetField('inlet_pressure')
        # this parameter indicates the reactants for this product may from other reactions
        self.__level_reactions = product_info.GetField('level_reactions')
        self.conversion = product_info.GetField('conversion')
        self.value_product = 0
        self.material = {}  # {chemical_id: FactoryReactant}

    def calculate_product_value(self, chemicals_info):
        self.value_product = UnitConversion.convert(chemicals_info[self.__product_chem_id].unit_cost,
                                                    chemicals_info[self.__product_chem_id].unit,
                                                    self.quantity_unit,
                                                    'QUALITY') * self.quantity

    def calculate_materials(self, reaction_formulas, chemicals_info):
        """
        calculate the necessary materials(quantity, cost(value)) for this product
        :return:
        """
        # todo: currently we do NOT consider the secondary reactions which produce the reactant for this product
        # step 0. convert the product quantity from unit(here is T)/year to moles/s
        moles_per_second = UnitConversion.convert(self.quantity, self.quantity_unit, 'g', 'QUALITY') \
                           / (chemicals_info[self.__product_chem_id].molar_mass * self.production_time)
        # step 1. get the reactants info from the reaction_formula
        if self.__reaction_formula_id in reaction_formulas:
            for chem_id, reactant in reaction_formulas[self.__reaction_formula_id].reactants.items():
                c = self.conversion
                formula = reactant.quantity_ratio
                # calculate the moles/s for the reactant using the ratio formula from database
                moles_reactant = eval(formula) * moles_per_second
                # convert moles/s to unit/year
                annual_quantity = UnitConversion.convert(chemicals_info[chem_id].molar_mass
                                                         * moles_reactant * self.production_time,
                                                         'g',
                                                         self.quantity_unit,
                                                         'QUALITY')
                # convert the unit_cost in chemical into the cost of the unit of the product * quantity
                annual_cost = UnitConversion.convert(chemicals_info[chem_id].unit_cost,
                                                     chemicals_info[chem_id].unit,
                                                     self.quantity_unit, 'QUALITY') * annual_quantity
                # add into material container
                self.material[chem_id] = FactoryMaterial(chemicals_info[chem_id].name, annual_quantity, -annual_cost)
        else:
            print("[ERROR]: No reaction formula is found for ", self.__reaction_formula_id)

    @property
    def product_name(self):
        return self.__chem_product_name_cn + "(" + self.__chem_product_name + ")"

    @property
    def production_time(self):
        # in seconds
        return UnitConversion.convert(self.days_of_production * self.hours_of_production, 'h', 's', 'TIME')

    @property
    def material_cost(self):
        rt_value = 0
        for v in self.material.values():
            rt_value += v.value
        return abs(rt_value)

    @property
    def revenue_per_year(self):
        return self.value_product - self.material_cost


class Factory:
    """
    this class contains all the information about the factory
    """
    def __init__(self, info):
        """
        :param info: dictionary format(json)
        """
        self.__id = info["id"]
        self.__name = info['properties']['name']
        self.__category = info['properties']['category']
        self.__geometry = info['geometry']
        self.__products = {}    # contains FactoryProduct

    def add_product(self, product_info, reaction_formulas, chemicals_info):
        """
        :param product_info: OGRFeature
        :param reaction_formulas: dictionary of all reaction formula's
        :param chemicals_info: dictionary of all chemicals
        :return:
        """
        product_chem_id = product_info.GetField('desired_chemical_id')
        if product_chem_id in chemicals_info:
            self.__products[product_chem_id] = FactoryProduct(product_chem_id, product_info)
            self.__products[product_chem_id].calculate_product_value(chemicals_info)
            self.__products[product_chem_id].calculate_materials(reaction_formulas, chemicals_info)
        else:
            print("[ERROR]: Unknown product. Please check the public.chemical table")

    @property
    def factory_id(self):
        return self.__id

    @property
    def factory_name(self):
        return self.__name


