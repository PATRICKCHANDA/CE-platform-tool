from .unit_conversion import UnitConversion


class ProcessComponent:
    """
    base class for Process-Product/ByProduct/Material
    """
    def __init__(self, chem_id, quantity, quantity_unit, name, value=0):
        self.chemical_id = chem_id
        self.name = name
        self.quantity = quantity
        self.quantity_unit = quantity_unit
        self.annual_value = value # < 0 means cost of buy, > 0 means product

    def component_json(self):
        return {'name': self.name,
                'quantity': self.quantity,
                'unit': self.quantity_unit,
                'annual_value': self.annual_value
                }


class ProcessByProduct(ProcessComponent):
    """
    a process's byproduct
    """
    def __init__(self, chem_id, name, quantity, quantity_unit, value):
        ProcessComponent.__init__(self, chem_id, quantity, quantity_unit, name, value)


class ProcessMaterial(ProcessComponent):
    """
    a process's (reaction) material
    """
    def __init__(self, chem_id, name, quantity, quantity_unit, value):
        ProcessComponent.__init__(self, chem_id, quantity, quantity_unit, name, value)


class ProcessProduct(ProcessComponent):
    """
    a process's product
    """
    def __init__(self, product_chem_id, quantity, unit, name):
        """
        initial the factory product
        :param product_chem_id:
        :param quantity:
        :param unit:
        :param name
        """
        ProcessComponent.__init__(self, product_chem_id, quantity, unit, name)
        self.moles_per_second = 1

    def calculate_product_value(self, chemical_info):
        self.annual_value = UnitConversion.convert(chemical_info.unit_cost,
                                                   chemical_info.unit,
                                                   self.quantity_unit,
                                                   'QUALITY') * self.quantity

    def calculate_materials(self, material, conversion, production_time, a_reaction_formula, chemicals_info):
        """
        calculate the necessary materials(quantity, cost(value)) for this product
        :param material: dictionary
        :param conversion: conversion value for product
        :param production_time: time of production (default: seconds)
        :param a_reaction_formula: instance of class ReactionFormula
        :param chemicals_info: dictionary of all chemicals
        :return:
        """
        # todo: currently we do NOT consider the secondary reactions which produce the reactant for this product
        # step 0. convert the product quantity from unit(here is T)/year to moles/s
        self.moles_per_second = UnitConversion.convert(self.quantity, self.quantity_unit, 'g', 'QUALITY') \
                           / (chemicals_info[self.chemical_id].molar_mass * production_time)
        # step 1. get the reactants info from the reaction_formula
        for chem_id, reactant in a_reaction_formula.reactants.items():
            c = conversion
            formula = reactant.quantity_ratio
            # calculate the moles/s for the reactant using the ratio formula from database
            moles_reactant = eval(formula) * self.moles_per_second
            # convert moles/s to unit/year
            annual_quantity = UnitConversion.convert(chemicals_info[chem_id].molar_mass
                                                     * moles_reactant * production_time,
                                                     'g',
                                                     self.quantity_unit,
                                                     'QUALITY')
            # convert the unit_cost in chemical into the cost of the unit of the product * quantity
            annual_cost = UnitConversion.convert(chemicals_info[chem_id].unit_cost,
                                                 chemicals_info[chem_id].unit,
                                                 self.quantity_unit, 'QUALITY') * annual_quantity
            # add into material container
            material[chem_id] = ProcessMaterial(chem_id, chemicals_info[chem_id].name, annual_quantity, self.quantity_unit, -annual_cost)


class FactoryProcess:
    """
    represent a FactoryProcess, it contains the process's products, materials, by-products, utilities-use,
    waste treatment
    """
    def __init__(self, **kwargs):
        self.rf_name = kwargs['rf_name']
        self.reaction_formula_id = kwargs['rf_id']
        self.days_of_production = kwargs['DOP']
        self.hours_of_production = kwargs['HOP']
        self.inlet_temperature = kwargs['inlet_T']
        self.inlet_pressure = kwargs['inlet_P']
        # this parameter indicates the reactants for this product may from other reactions
        self.__level_reactions = kwargs['level_R']
        self.conversion = kwargs['conversion']
        self.__products = dict()    # contains ProcessProduct per reaction_formula
        self.__byproducts = {}      # {chemical_id: ProcessByProduct}
        self.__material = {}        # {chemical_id: ProcessMaterial}
        self.__utility = {}
        # indicate the material is already added, if true, when the next product added for this process, we do not need
        # to calculate the material again!
        self.__material_added = False

    def add_product(self, product_chemical_id, quantity, unit, rf_info, all_chem_info):
        """
        create ProcessProduct, which contains the desired product, byproducts, material information
        :param product_chemical_id:
        :param quantity:
        :param unit:
        :param rf_info: a reaction_formula instance
        :param all_chem_info: dictionary of all chemical
        :return:
        """
        # add the desired product of this reaction
        a_product = ProcessProduct(product_chemical_id,
                                   quantity,
                                   unit,
                                   all_chem_info[product_chemical_id].name
                                   )
        a_product.calculate_product_value(all_chem_info[product_chemical_id])
        if not self.__material_added:
            # get the by-products of this reaction formula
            a_product.calculate_materials(self.__material,
                                          self.conversion,
                                          self.production_time,
                                          rf_info,
                                          all_chem_info
                                          )
            # set material is added
            self.__material_added = True
        self.__products[product_chemical_id] = a_product

    def add_byproducts(self, all_rf_info, all_chem_info):
        """
        add byproducts
        :param all_rf_info:
        :param all_chem_info:
        :return: list of byproducts name
        """
        a_reaction_formula = all_rf_info[self.reaction_formula_id]
        # step 0. get all the products info from the reaction_formula, the reaction_product with quantity is '1' moles
        # is the reference product, since the quantity of all other products is based on this
        a_product = None
        for chem_id, rf_product in a_reaction_formula.products.items():
            if rf_product.quantity == '1' and chem_id in self.__products:
                # use this product as reference product, in the database we have made sure this is one of the desired
                # product with quantity as 1
                a_product = self.__products[chem_id]
                break

        # step 1. take one product from this FactoryProcess(reaction formula), if not a product, then it is a
        # byproduct
        byproduct_names = []
        for chem_id, rf_product in a_reaction_formula.products.items():
            # chem_id not in the products, then consider it as byproduct
            if chem_id not in self.__products:
                c = self.conversion
                # calculate the moles/s for the reactant using the ratio formula from database
                formula = rf_product.quantity
                moles_byproduct = eval(formula) * a_product.moles_per_second
                # convert moles/s to unit/year
                annual_quantity = UnitConversion.convert(all_chem_info[chem_id].molar_mass
                                                         * moles_byproduct * self.production_time,
                                                         'g',
                                                         a_product.quantity_unit,
                                                         'QUALITY')
                # convert the unit_cost in chemical into the cost of the unit of the product * quantity
                annual_cost = UnitConversion.convert(all_chem_info[chem_id].unit_cost,
                                                     all_chem_info[chem_id].unit,
                                                     a_product.quantity_unit, 'QUALITY') * annual_quantity
                self.__byproducts[chem_id] = ProcessByProduct(chem_id,
                                                              all_chem_info[chem_id].name,
                                                              annual_quantity,
                                                              a_product.quantity_unit,
                                                              -annual_cost
                                                              )
                byproduct_names.append(all_chem_info[chem_id].name)
        return byproduct_names

    @property
    def products(self):
        return self.__products

    @property
    def production_time(self):
        # in seconds
        return UnitConversion.convert(self.days_of_production * self.hours_of_production, 'h', 's', 'TIME')

    @property
    def material_cost(self):
        """
        :return: cost of all material of the process
        """
        return abs(sum(v.annual_value for v in self.__material.values()))

    @property
    def byproducts_cost(self):
        """
        :return: cost all byproducts of the process
        """
        return abs(sum(v.annual_value for v in self.__byproducts.values()))

    @property
    def products_value(self):
        """
        :return: value of all products of the process
        """
        return sum(p.annual_value for p in self.__products.values())

    @property
    def revenue_per_year(self):
        """
        a product line revenue: products - material - byproducts - ...
        :return:
        """
        return self.products_value - self.material_cost - self.byproducts_cost

    def factory_process_json(self):
        """
        :return: dictionary of factory process information
        """
        return {'rf_name': self.rf_name,
                'DOP': self.days_of_production,
                'HOP': self.hours_of_production,
                'inlet_T': self.inlet_temperature,
                'inlet_P': self.inlet_pressure,
                'conversion': self.conversion,
                'products': [p.component_json for p in self.__products.values()],
                'by-products': [p.component_json for p in self.__byproducts.values()],
                'material': [p.component_json for p in self.__material.values()],
                'process_annual_revenue': self.revenue_per_year
                }


class Factory:
    """
    this class contains all the information about the factory
    """
    def __init__(self, info):
        """
        :param info: dictionary format(json)
        """
        # self.__factory_json = info  # all factory information in dictionary
        self.__id = info["id"]
        self.__name = info['properties']['name']
        self.__category = info['properties']['category']
        self.__geometry = info['geometry']
        # per product line represent 1 reaction_formula
        self.__product_lines = {}

    def add_product_line(self, factory_reaction_info, rf_id, reaction_formulas_info, chemicals_info):
        """
        for each unique reaction formula, create a FactoryProcess
        :param factory_reaction_info: OGRFeature
        :param rf_id: key for reaction_formula_info dictionary
        :param reaction_formulas_info: dictionary of all reaction formula's
        :param chemicals_info: dictionary of all chemicals
        :return:
        """
        product_chem_id = factory_reaction_info.GetField('desired_chemical_id')
        chem_name = factory_reaction_info.GetField('name_en')
        chem_name_cn = factory_reaction_info.GetField('name_cn')
        quantity = factory_reaction_info.GetField('desired_quantity')
        quantity_unit = factory_reaction_info.GetField('unit')

        # per reaction formula may have more than 1 products (although the chance is small?), in this case, all the
        # products share the same material
        if rf_id not in self.__product_lines:
            # setup the FactoryProcess with basic process information
            self.__product_lines[rf_id] = FactoryProcess(rf_name=reaction_formulas_info[rf_id].name,
                                                         rf_id=rf_id,
                                                         DOP=factory_reaction_info.GetField('days_of_production'),
                                                         HOP=factory_reaction_info.GetField('hours_of_production'),
                                                         inlet_T=factory_reaction_info.GetField('inlet_temperature'),
                                                         inlet_P=factory_reaction_info.GetField('inlet_pressure'),
                                                         level_R=factory_reaction_info.GetField('level_reactions'),
                                                         conversion=factory_reaction_info.GetField('conversion')
                                                         )
        # add the target product
        self.__product_lines[rf_id].add_product(product_chem_id,
                                                quantity,
                                                quantity_unit,
                                                reaction_formulas_info[rf_id],
                                                chemicals_info
                                                )

    @property
    def factory_product_lines(self):
        return self.__product_lines

    @property
    def factory_id(self):
        return self.__id

    @property
    def factory_name(self):
        return self.__name

    @property
    def factory_json(self):
        return {'type': 'Feature',
                'geometry': self.__geometry,
                'id': self.factory_id,
                'properties': {'name': self.factory_name,
                               'category': self.__category
                               }
                }


