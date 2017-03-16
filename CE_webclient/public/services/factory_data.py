from .unit_conversion import UnitConversion

HEAT_CAPACITY_RATIO = 1.4


class ProcessComponent:
    """
    base class for Process-Product/ByProduct/Material
    """
    def __init__(self, comp_id, mps, quantity, quantity_unit, name, value_unit, value=0.0):
        """
        :param comp_id: chemical_id / utility_type_id
        :param mps: moles per second
        :param quantity:
        :param quantity_unit:
        :param name:
        :param value_unit
        :param value:
        """
        self.component_id = comp_id
        self.name = name
        self.moles_per_second = mps
        self.quantity = quantity    # Tonnes/year
        self.quantity_unit = quantity_unit
        self.annual_value = value   # < 0 means cost of buy, > 0 means product
        self.value_unit = value_unit    # currency symbol

    @property
    def component_json(self):
        return {'id': self.component_id,
                'name': self.name,
                'quantity': self.quantity,
                'unit': self.quantity_unit,
                'annual_value': self.annual_value,
                'currency': self.value_unit
                }


class ProcessByProduct(ProcessComponent):
    """
    a process's byproduct
    """
    def __init__(self, chem_id, name, mps, quantity, quantity_unit, value_unit, value):
        ProcessComponent.__init__(self, chem_id, mps, quantity, quantity_unit, name, value_unit, value)


class ProcessMaterial(ProcessComponent):
    """
    a process's (reaction) material
    """
    def __init__(self, chem_id, name, mps, quantity, quantity_unit, value_unit, value):
        ProcessComponent.__init__(self, chem_id, mps, quantity, quantity_unit, name, value_unit, value)


class ProcessProduct(ProcessComponent):
    """
    a process's product
    """
    def __init__(self, product_chem_id, quantity, quantity_unit, name, value_unit):
        """
        initial the factory product
        :param product_chem_id:
        :param quantity:
        :param quantity_unit:
        :param name:
        :param value_unit: currency symbol
        """
        ProcessComponent.__init__(self, product_chem_id, 1, quantity, quantity_unit, name, value_unit)

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
                           / (chemicals_info[self.component_id].molar_mass * production_time)
        # step 1. get the reactants info from the reaction_formula
        for chem_id, reactant in a_reaction_formula.reactants.items():
            if chem_id not in chemicals_info:
                print("[ERROR] in function calculate_material(): Unknown chemical [", chem_id, "] in the database")
                continue
            chem_info = chemicals_info[chem_id]
            c = conversion
            formula = reactant.quantity_ratio
            # calculate the moles/s for the reactant using the ratio formula from database
            moles_reactant = eval(formula) * self.moles_per_second
            # convert moles/s to unit/year
            annual_quantity = UnitConversion.convert(chem_info.molar_mass * moles_reactant * production_time,
                                                     'g',
                                                     self.quantity_unit,
                                                     'QUALITY')
            # convert the unit_cost in chemical into the cost of the unit of the product * quantity
            annual_cost = UnitConversion.convert(chem_info.unit_cost,
                                                 chem_info.unit,
                                                 self.quantity_unit, 'QUALITY') * annual_quantity
            # add into material container
            material[chem_id] = ProcessMaterial(chem_id,
                                                chem_info.name,
                                                moles_reactant,
                                                annual_quantity,
                                                self.quantity_unit,
                                                chem_info.currency,
                                                -annual_cost
                                                )


class FactoryProcess:
    """
    represent a FactoryProcess, it contains the process's products, materials, by-products, utilities-use,
    waste treatment
    """
    def __init__(self, **kwargs):
        self.rf_info = kwargs['rf_info']
        self.rf_name = self.rf_info.name
        self.days_of_production = kwargs['DOP']
        self.hours_of_production = kwargs['HOP']
        self.inlet_temperature = kwargs['inlet_T']
        self.inlet_pressure = kwargs['inlet_P']
        # this parameter indicates the reactants for this product may from other reactions
        self.__level_reactions = kwargs['level_R']
        self.conversion = kwargs['conversion']
        self.percent_heat_removed_by_cooling_tower = kwargs['perc_heat_removed']
        # reference product chem id: in the DB, one of ReactionFormula's products has quantity equal to '1',
        # and all other products' quantity of this RF is based on the reference product
        self.__ref_product_chem_id = None
        self.__products = dict()    # contains ProcessProduct per reaction_formula
        self.__byproducts = {}      # {chemical_id: ProcessByProduct instance}
        self.__material = {}        # {chemical_id: ProcessMaterial instance}
        self.__utility = {}         # {utility_type_id: ProcessComponent instance}
        self.__emission = {}        # {name: quantity}
        # indicate the material is already added, if true, when the next product added for this process, we do not need
        # to calculate the material again! So, different products of the process share the same material!
        # Only calculate once!
        self.__material_added = False

    def add_product(self, product_chemical_id, quantity, unit, all_chem_info):
        """
        create a ProcessProduct, and calculate its value and also required material information
        :param product_chemical_id:
        :param quantity:
        :param unit:
        :param all_chem_info: dictionary of all chemical
        :return:
        """
        # add the desired product of this reaction
        a_product = ProcessProduct(product_chemical_id,
                                   quantity,
                                   unit,
                                   all_chem_info[product_chemical_id].name,
                                   all_chem_info[product_chemical_id].currency
                                   )
        # determine the reference product: to be used when calculate byproducts, since in the DB, all other products
        # of this reaction is based on the reference product
        if self.rf_info.products[product_chemical_id].quantity == '1':
            self.__ref_product_chem_id = product_chemical_id

        a_product.calculate_product_value(all_chem_info[product_chemical_id])
        if not self.__material_added:
            # get the by-products of this reaction formula
            a_product.calculate_materials(self.__material,
                                          self.conversion,
                                          self.production_time,
                                          self.rf_info,
                                          all_chem_info
                                          )
            # set material is added
            self.__material_added = True
        self.__products[product_chemical_id] = a_product

    def add_byproducts(self, all_chem_info):
        """
        add byproducts for this process, different products of the process share the same material
        :param all_chem_info:
        :return: list of byproducts name
        """
        # step 0. get all the products info from the reaction_formula, the reaction_product with quantity is '1' moles
        # is the reference product, since the quantity of all other products is based on this
        a_product = self.__products[self.__ref_product_chem_id]

        # step 1. take one product from this FactoryProcess(reaction formula), if not a product, then it is a
        # byproduct
        byproduct_names = []
        for chem_id, rf_product in self.rf_info.products.items():
            # check
            if chem_id not in all_chem_info:
                print("[ERROR] in function add_byproducts(): Unknown chemical [", chem_id, "] in the database")

            # chem_id not in the products(which means it is not in the factory_reaction_product table,
            # then consider it as byproduct
            if chem_id not in self.__products:
                chem_info = all_chem_info[chem_id]
                c = self.conversion
                # calculate the moles/s for the reactant using the ratio formula from database
                formula = rf_product.quantity
                moles_byproduct = eval(formula) * a_product.moles_per_second
                # convert moles/s to unit/year
                annual_quantity = UnitConversion.convert(chem_info.molar_mass * moles_byproduct * self.production_time,
                                                         'g',
                                                         a_product.quantity_unit,
                                                         'QUALITY')
                # convert the unit_cost in chemical into the cost of the unit of the product * quantity
                annual_cost = UnitConversion.convert(chem_info.unit_cost, chem_info.unit,
                                                     a_product.quantity_unit, 'QUALITY') * annual_quantity
                # save as ProcessByProduct
                self.__byproducts[chem_id] = ProcessByProduct(chem_id,
                                                              chem_info.name,
                                                              moles_byproduct,
                                                              annual_quantity,
                                                              a_product.quantity_unit,
                                                              chem_info.currency,
                                                              -annual_cost
                                                              )
                byproduct_names.append(all_chem_info[chem_id].name)
        return byproduct_names

    def calculate_process_emission(self, emission_data):
        """
        calculate the process emission based on the emission_data
        :param emission_data: list of EmissionData instance
        :return:
        """
        if self.__ref_product_chem_id is not None:
            a_product = self.__products[self.__ref_product_chem_id]
            for emis_data in emission_data:
                self.__emission[emis_data.name] = emis_data.total * a_product.quantity  # todo: kg/kg * tonnes/year

    # todo: need validation by collega's and the structure and data may be changed!
    def calculate_process_utilities(self, all_utility_info, all_chem_info):
        volume_flow = 0
        heat_thermal_mass = 0
        for material in self.__material.values():
            chem_info = all_chem_info[material.component_id]
            molar_mass_kg = UnitConversion.convert(chem_info.molar_mass, 'g', 'kg', 'QUALITY')
            # sum the volume flow of the material
            try:
                volume_flow += material.moles_per_second * molar_mass_kg * 3600 / chem_info.density
                # sum the thermal mass
                heat_thermal_mass += UnitConversion.convert(
                    molar_mass_kg * material.moles_per_second * chem_info.sp_heat
                    * (self.rf_info.temperature - self.inlet_temperature),
                    'J',
                    'kWh',
                    'ENERGY'
                    )
            except ZeroDivisionError or TypeError:
                print("[Error]: Missing density or SP_heat information for ", chem_info.name,
                      " in FactoryProcess.calculate_process_utilities()")
                return

        # compressor sizing, 1 bars = 100 Kpa
        tmp = HEAT_CAPACITY_RATIO / (HEAT_CAPACITY_RATIO - 1)
        Pad = 2.78 * 1E-4 * volume_flow * self.inlet_pressure * 100 * tmp * \
              (pow(self.rf_info.pressure / self.inlet_pressure, 1.0/tmp) - 1)
        # step 0: get the amount
        # electricity
        electricity = UnitConversion.convert(Pad, 'kJ', 'kWh', 'ENERGY')
        # heat reaction
        c = self.conversion     # c is used in the self.rf_info.heat_reaction_formula
        heat_reaction = UnitConversion.convert(eval(self.rf_info.heat_reaction_formula) * self.__products[self.__ref_product_chem_id].moles_per_second,
                                               'kJ', 'kWh', 'ENERGY')
        # make up water
        make_up_water = UnitConversion.convert(self.percent_heat_removed_by_cooling_tower * (abs(heat_reaction) + abs(heat_thermal_mass)),
                                               'kWh', 'J', 'ENERGY') / (2.26 * 1E6)
        # water treatment
        water_treatment = UnitConversion.convert(self.percent_heat_removed_by_cooling_tower *
                                                 (abs(heat_reaction) + abs(heat_thermal_mass)), 'kWh', 'GJ', 'ENERGY')

        # step 1: calculate the cost of different utilities
        for obj_id in self.__utility.keys():
            an_utility_info = all_utility_info[obj_id]
            utility_name = an_utility_info.name_en.lower().strip()
            value_unit = an_utility_info.currency
            if utility_name == "electricity":
                self.__utility[obj_id] = ProcessComponent(obj_id, None, electricity,
                                                          an_utility_info.unit,
                                                          utility_name,
                                                          value_unit,
                                                          electricity * an_utility_info.unit_cost * self.production_time
                                                          )
            elif utility_name == "heat reaction":
                cost_per_year = (1.0 - self.percent_heat_removed_by_cooling_tower)\
                                * heat_reaction \
                                * an_utility_info.unit_cost \
                                * self.production_time
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          heat_reaction,
                                                          an_utility_info.unit,
                                                          utility_name,
                                                          value_unit,
                                                          cost_per_year
                                                          )
            elif utility_name == "heat thermal":
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          heat_thermal_mass,
                                                          an_utility_info.unit,
                                                          utility_name,
                                                          value_unit,
                                                          heat_thermal_mass * an_utility_info.unit_cost
                                                          * self.production_time
                                                          )
            elif utility_name == "make up water":
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          make_up_water,
                                                          an_utility_info.unit,
                                                          utility_name,
                                                          value_unit,
                                                          make_up_water * an_utility_info.unit_cost
                                                          * self.production_time
                                                          )
            elif utility_name == "water treatment":
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          water_treatment,
                                                          an_utility_info.unit,
                                                          utility_name,
                                                          value_unit,
                                                          water_treatment * an_utility_info.unit_cost
                                                          * self.production_time
                                                          )
            else:
                print("[Warning:] Unknown ", utility_name)

    @property
    def products(self):
        return self.__products

    @property
    def utilities(self):
        return self.__utility

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
        a product line revenue: products - material - byproducts - utility...
        :return:
        """
        return self.products_value - self.material_cost - self.byproducts_cost - self.utilities_cost

    @property
    def utilities_cost(self):
        """
        :return: cost of all utilities
        """
        return sum(u.annual_value for u in self.__utility.values())

    @property
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
                'emissions': self.__emission,
                'utilities': [p.component_json for p in self.__utility.values()],
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
        if product_chem_id not in chemicals_info:
            print('[ERROR] in function add_product_line(): Unknown chemical [', product_chem_id, '] in the database')
            return

        quantity = factory_reaction_info.GetField('desired_quantity')
        quantity_unit = factory_reaction_info.GetField('unit')

        # per reaction formula may have more than 1 products (although the chance is small?), in this case, all the
        # products share the same material
        if rf_id not in self.__product_lines:
            # setup the FactoryProcess with basic process information
            self.__product_lines[rf_id] = FactoryProcess(rf_info=reaction_formulas_info[rf_id],
                                                         DOP=factory_reaction_info.GetField('days_of_production'),
                                                         HOP=factory_reaction_info.GetField('hours_of_production'),
                                                         inlet_T=factory_reaction_info.GetField('inlet_temperature'),
                                                         inlet_P=factory_reaction_info.GetField('inlet_pressure'),
                                                         level_R=factory_reaction_info.GetField('level_reactions'),
                                                         conversion=factory_reaction_info.GetField('conversion'),
                                                         perc_heat_removed=factory_reaction_info.GetField('percent_heat_removed')
                                                         )
        # add the target product
        self.__product_lines[rf_id].add_product(product_chem_id,
                                                quantity,
                                                quantity_unit,
                                                chemicals_info
                                                )

    def calculate_byproducts_per_product_line(self, chemicals_info):
        """
        calculate byproducts per product line in the factory
        :param chemicals_info:
        :return:
        """
        for rf_id, product_line in self.factory_product_lines.items():
            list_byproducts = product_line.add_byproducts(chemicals_info)
            print(list_byproducts,
                  " byproducts are added for ",
                  product_line.rf_info.name,
                  ' for ',
                  self.factory_name
                  )

    def calculate_emission_per_product_line(self, all_emission_data):
        for rf_id, product_line in self.__product_lines.items():
            product_line.calculate_process_emission(all_emission_data[rf_id])

    def calculate_utilities_per_product_line(self, all_utility_info, all_chem_info):
        """
        calculate all utilities for each product line (FactoryProcess), call this function when all data is read
        from factory_reaction_utility table
        :param all_utility_info:
        :param all_chem_info:
        :return:
        """
        for product_line in self.__product_lines.values():
            product_line.calculate_process_utilities(all_utility_info, all_chem_info)

    def store_utilities(self, a_rf_id, utility_obj_id):
        """
        store the utilities that a process is used by the factory, no calculation!
        :param a_rf_id:
        :param utility_obj_id:
        :return:
        """
        if a_rf_id in self.__product_lines:
            self.__product_lines[a_rf_id].utilities[utility_obj_id] = None
        else:
            print('[WARNING] in function store_utilities: unknown ', a_rf_id, ' in Factory production line')

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
    def factory_revenue(self):
        """
        :return: total revenue of the factory
        """
        rt_value = 0
        for product_line in self.__product_lines.values():
            rt_value += product_line.revenue_per_year
        return rt_value

    @property
    def factory_basic_info_json(self):
        return {'type': 'Feature',
                'geometry': self.__geometry,
                'id': self.factory_id,
                'properties': {'name': self.factory_name,
                               'category': self.__category
                               }
                }

    def get_a_factory_process_json(self, rf_id):
        """
        :param rf_id: reaction formula id or a product_line
        :return: dictionary of the specified FactoryProcess (json format)
        """
        return self.__product_lines[rf_id].factory_process_json

    @property
    def factory_products_json(self):
        return [(rf_id, product.factory_process_json) for rf_id, product in self.__product_lines.items()]