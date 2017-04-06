from .unit_conversion import UnitConversion

HEAT_CAPACITY_RATIO = 1.4
MEGA = "M"
NUM_DIGITS = 0


class ProcessComponent:
    """
    base class for Process-Product/ByProduct/Material
    """
    def __init__(self, comp_id, mps, quantity, quantity_unit, name, value_per_unit, currency, value=0.0):
        """
        :param comp_id: chemical_id / utility_type_id
        :param mps: moles per second
        :param quantity: annual quantity
        :param quantity_unit:
        :param name:
        :param unit_value: value per unit
        :param currency
        :param value:
        """
        self.component_id = comp_id
        self.name = name
        self.moles_per_second = mps
        self.quantity = quantity    # Tonnes/year
        self.quantity_unit = quantity_unit
        self.annual_value = value   # < 0 means cost of buy, > 0 means profit
        self.value_per_unit = value_per_unit
        self.currency = currency    # currency symbol

    def update(self, comp_id, mps, quantity, quantity_unit, value_per_unit, currency, value):
        """
        update the component information
        :param comp_id: 
        :param mps: 
        :param quantity: 
        :param quantity_unit: 
        :param value_per_unit: 
        :param currency: 
        :param value: 
        :return: 
        """
        if comp_id != self.component_id:
            return False
        self.moles_per_second = mps
        self.quantity = quantity    # Tonnes/year
        self.quantity_unit = quantity_unit
        self.annual_value = value   # < 0 means cost of buy, > 0 means profit
        self.value_per_unit = value_per_unit
        self.currency = currency    # currency symbol
        return True

    @property
    def component_json(self):
        if self.currency is None:
            return {'id': self.component_id,
                    'name': self.name,
                    'quantity': round(self.quantity, NUM_DIGITS),
                    'unit': self.quantity_unit,
                    'value_per_unit': self.value_per_unit,
                    'currency_value_per_unit': self.currency,
                    'annual_value': round(self.annual_value, NUM_DIGITS),
                    'currency': self.currency
                    }
        else:
            new_currency_unit = MEGA + self.currency
            new_value = UnitConversion.convert(self.annual_value, self.currency, new_currency_unit, "CURRENCY")
            # self.value_unit = new_value_unit
            return {'id': self.component_id,
                    'name': self.name,
                    'quantity': round(self.quantity, NUM_DIGITS),
                    'unit': self.quantity_unit,
                    'value_per_unit': self.value_per_unit,
                    'currency_value_per_unit': self.currency,
                    'annual_value': round(new_value, NUM_DIGITS),
                    'currency': new_currency_unit
                    }

    def calculate_quantity(self, molar_mass, production_time):
        self.quantity = UnitConversion.convert(molar_mass * self.moles_per_second * production_time,
                                               'g', self.quantity_unit, 'QUALITY')
    def calculate_moles_per_second(self, molar_mass, production_time):
        self.moles_per_second = UnitConversion.convert(self.quantity, self.quantity_unit, 'g', 'QUALITY') \
        / (molar_mass * production_time)


class ProcessByProduct(ProcessComponent):
    """
    a process's byproduct
    """
    def __init__(self, chem_id, name, mps, quantity, quantity_unit, value_per_unit, currency, value):
        ProcessComponent.__init__(self, chem_id, mps, quantity, quantity_unit, name, value_per_unit, currency, value)


class ProcessMaterial(ProcessComponent):
    """
    a process's (reaction) material
    """
    def __init__(self, chem_id, name, mps, quantity, quantity_unit, value_per_unit, currency, value):
        ProcessComponent.__init__(self, chem_id, mps, quantity, quantity_unit, name, value_per_unit, currency, value)


class ProcessProduct(ProcessComponent):
    """
    a process's product
    """
    def __init__(self, product_chem_id, quantity, quantity_unit, name, value_per_unit, currency):
        """
        initial the factory product
        :param product_chem_id:
        :param quantity:
        :param quantity_unit:
        :param name: product name
        :param value_per_unit: value per unit
        :param currency: currency symbol
        """
        ProcessComponent.__init__(self, product_chem_id, 1, quantity, quantity_unit, name, value_per_unit, currency)

    def calculate_product_value(self, chemical_info, local_unit_cost=None):
        """       
        :param chemical_info: 
        :param local_unit_cost: a local price instead of global price 
        :return: 
        """
        value_per_unit = chemical_info.unit_cost
        if local_unit_cost is not None:
            value_per_unit = local_unit_cost
        # convert kost per gram to kost per T
        self.annual_value = UnitConversion.convert(value_per_unit,
                                                   chemical_info.unit,
                                                   self.quantity_unit,
                                                   'QUALITY') * self.quantity

    def calculate_materials(self, mps, material, conversion, production_time, a_reaction_formula, chemicals_info, update=False):
        """
        calculate the necessary materials(quantity, cost(value)) for this product
        :param mps: moles per second of the REFERENCE product
        :param material: dictionary to store the added material details
        :param conversion: conversion value for product
        :param production_time: time of production (default: seconds)
        :param a_reaction_formula: instance of class ReactionFormula
        :param chemicals_info: dictionary of all chemicals
        :param update: if true, create new ProcessMaterial instance, otherwise update the existing ProcessMaterial
        :return: boolean
        """
        # todo: currently we do NOT consider the secondary reactions which produce the reactant for this product
        # step 0. convert the product quantity from unit(here is T)/year to moles/s
        self.calculate_moles_per_second(chemicals_info[self.component_id].molar_mass, production_time)
        # step 1. loop through all the reactants info from the reaction_formula, they are all materials!
        for chem_id, reactant in a_reaction_formula.reactants.items():
            if chem_id not in chemicals_info:
                print("[ERROR] in function calculate_material(): Unknown chemical [", chem_id, "] in the database")
                continue
            chem_info = chemicals_info[chem_id]
            # this variable is use by eval() function and should be called 'c'
            c = conversion
            formula = reactant.quantity_ratio
            # calculate the moles/s for the reactant using the ratio formula from database
            moles_reactant = eval(formula) * mps
            # convert moles/s to unit/year
            annual_quantity = UnitConversion.convert(chem_info.molar_mass * moles_reactant * production_time,
                                                     'g',
                                                     self.quantity_unit,
                                                     'QUALITY')
            # convert the unit_cost in chemical into the cost of the unit of the product * quantity
            annual_cost = UnitConversion.convert(chem_info.unit_cost,
                                                 chem_info.unit,
                                                 self.quantity_unit, 'QUALITY') * annual_quantity
            if update and chem_id not in material:
                print("[ERROR]: Failed to update material ", chem_info.name, " for reaction ",
                      a_reaction_formula.name)
                return False
            # add into material container
            material[chem_id] = ProcessMaterial(chem_id,
                                                chem_info.name,
                                                moles_reactant,
                                                annual_quantity,
                                                self.quantity_unit,
                                                chem_info.unit_cost,
                                                chem_info.currency,
                                                -annual_cost
                                                )
        return True


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
        self.__products = dict()    # contains ProcessProduct per reaction_formula {chemical_id, ProcessProduct}
        self.__byproducts = {}      # {chemical_id: ProcessByProduct instance}
        self.__material = {}        # {chemical_id: ProcessMaterial instance}
        self.__utility = {}         # {utility_type_id: ProcessComponent instance}
        self.__emission = {}        # {name: quantity}
        # indicate the material is already added, if true, when the next product added for this process, we do not need
        # to calculate the material again! So, different products of the ONE process share the same material!
        # Only calculate once!
        self.__material_added = False
        # reference product chem id: in the DB, one of ReactionFormula's products has quantity equal to '1',
        # and all other products' quantity of this RF is based on the reference product
        self.__ref_product = None
        self.__ref_product_chem_id = None
        for chem_id, detail in self.rf_info.products.items():
            if detail.quantity == '1':
                self.__ref_product_chem_id = chem_id
                break
        if self.__ref_product_chem_id is None:
            raise ValueError("Cannot find a reference product in the defined process.")

    def add_product(self, product_chemical_id, quantity, unit, all_chem_info, new_product_line):
        """
        create a ProcessProduct, and calculate its value and also required material information
        :param product_chemical_id:
        :param quantity:
        :param unit: quantity unit
        :param all_chem_info: dictionary of all chemical
        :param new_product_line: True means the product line existed, the new product_chemical_id's quantity
                                 should consistent with the reference product of this process
        :return:
        """
        if not new_product_line and self.__ref_product is None:
            raise ValueError("No existed reference product in the product line")

        curt_chem_info = all_chem_info[product_chemical_id]
        a_product = ProcessProduct(product_chemical_id,
                                   quantity,
                                   unit,
                                   curt_chem_info.name,
                                   curt_chem_info.unit_cost,
                                   curt_chem_info.currency
                                   )
        a_product.calculate_moles_per_second(curt_chem_info.molar_mass, self.production_time)

        # create the reference product: to be used when calculate byproducts, since in the DB,
        # all other products/emission/utility/material of this reaction is based on the reference product
        if self.__ref_product is None:
            ref_chem_info = all_chem_info[self.__ref_product_chem_id]
            self.create_a_reference_product(a_product, ref_chem_info, product_chemical_id, quantity, unit)

        # if this product is an existed process, then the ref_product should already be created
        if not new_product_line:
            # update the moles per second to consistent with reference
            c = self.conversion
            formula = self.rf_info.products[product_chemical_id].quantity
            a_product.moles_per_second = self.__ref_product.moles_per_second * eval(formula)
            # update its quantity
            a_product.calculate_quantity(curt_chem_info.molar_mass, self.production_time)

        a_product.calculate_product_value(all_chem_info[product_chemical_id])
        if not self.__material_added:
            # get the by-products of this reaction formula
            a_product.calculate_materials(self.__ref_product.moles_per_second,
                                          self.__material,
                                          self.conversion,
                                          self.production_time,
                                          self.rf_info,
                                          all_chem_info,
                                          False  # creation
                                          )
            # set material is added
            self.__material_added = True
        self.__products[product_chemical_id] = a_product

    def create_a_reference_product(self, a_product, ref_chem_info, product_chemical_id, quantity, unit):
        self.__ref_product = ProcessProduct(self.__ref_product_chem_id,
                                            quantity,
                                            unit,
                                            ref_chem_info.name,
                                            ref_chem_info.unit_cost,
                                            ref_chem_info.currency
                                            )
        if self.__ref_product_chem_id != product_chemical_id:
            c = self.conversion
            formula = self.rf_info.products[product_chemical_id].quantity
            # calculate moles per second for the reference product in this product line
            self.__ref_product.moles_per_second = a_product.moles_per_second / eval(formula)
            # and update the quantity
            self.__ref_product.calculate_quantity(ref_chem_info.molar_mass, self.production_time)
            self.__ref_product.calculate_product_value(ref_chem_info)

    def calculate_byproducts(self, all_chem_info, update=False):
        """
        add byproducts for this process, different products of the process share the same material
        :param all_chem_info:
        :param update: if true, check whether the byproduct already added
        :return: list of byproducts name
        """
        # step 0. get all the products info from the reaction_formula, the reaction_product with quantity is '1' moles
        # is the reference product, since the quantity of all other products is based on this
        a_product = self.__ref_product

        # step 1. take one product from this FactoryProcess(reaction formula), if not a product, then it is a
        # byproduct
        byproduct_names = []
        for chem_id, rf_product in self.rf_info.products.items():
            # check
            if chem_id not in all_chem_info:
                print("[ERROR] in function calculate_byproducts(): Unknown chemical [", chem_id, "] in the database")

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

                if update and chem_id not in self.__byproducts:
                    print("[ERROR]: Failed to update byproduct ", chem_info.name, " for reaction ", self.rf_name)
                    return None
                # save as ProcessByProduct
                self.__byproducts[chem_id] = ProcessByProduct(chem_id,
                                                              chem_info.name,
                                                              moles_byproduct,
                                                              annual_quantity,
                                                              a_product.quantity_unit,
                                                              chem_info.unit_cost,
                                                              chem_info.currency,
                                                              -annual_cost
                                                              )
                byproduct_names.append(all_chem_info[chem_id].name)
        return byproduct_names, True

    def calculate_process_emission(self, emission_data, update=False):
        """
        calculate the process emission based on the emission_data
        :param emission_data: list of EmissionData instance
        :param update: if True, check whether the emission already added
        :return:
        """
        if self.__ref_product_chem_id is not None:
            a_product = self.__ref_product
            for emis_data in emission_data:
                if update and emis_data.name not in self.__emission:
                    print("[ERROR]: Failed to update emission ", emis_data.name, " for reaction ", self.rf_name)
                    return False
                self.__emission[emis_data.name] = ProcessComponent(-1, None, emis_data.total * a_product.quantity,
                                                                   a_product.quantity_unit,
                                                                   emis_data.name,
                                                                   None, None)
            return True

    # todo: utility calculation needs validation by collega's and the structure and data may be changed!
    def calculate_process_utilities(self, all_utility_info, all_chem_info):
        if self.__utility is None or  len(self.__utility) == 0:
            return True
        volume_flow = 0
        heat_thermal_mass = 0
        for material in self.__material.values():
            # catalyst will not be considered
            if self.rf_info.reactants[material.component_id].is_catalyst:
                continue
            chem_info = all_chem_info[material.component_id]
            molar_mass_kg = UnitConversion.convert(chem_info.molar_mass, 'g', 'kg', 'QUALITY')
            # sum the volume flow of the material
            try:
                # unit: m3/hr
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
        # unit: KJ
        Pad = 2.78 * 1E-4 * volume_flow * self.inlet_pressure * 100 * tmp * \
              (pow(self.rf_info.pressure / self.inlet_pressure, 1.0/tmp) - 1)
        # step 0: get the amount
        # electricity: units/sec
        electricity = UnitConversion.convert(Pad, 'kJ', 'kWh', 'ENERGY')
        # heat reaction
        c = self.conversion     # c is used in the self.rf_info.heat_reaction_formula
        heat_reaction = UnitConversion.convert(eval(self.rf_info.heat_reaction_formula) * self.__ref_product.moles_per_second,
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
            currency_unit = an_utility_info.currency
            if utility_name == "electricity":
                self.__utility[obj_id] = ProcessComponent(obj_id, None, electricity * self.production_time,
                                                          an_utility_info.unit,
                                                          an_utility_info.name,
                                                          an_utility_info.unit_cost,
                                                          currency_unit,
                                                          -electricity * an_utility_info.unit_cost * self.production_time
                                                          )
            elif utility_name == "heat reaction":
                cost_per_year = (1.0 - self.percent_heat_removed_by_cooling_tower)\
                                * heat_reaction \
                                * an_utility_info.unit_cost \
                                * self.production_time
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          heat_reaction * self.production_time,
                                                          an_utility_info.unit,
                                                          an_utility_info.name,
                                                          an_utility_info.unit_cost,
                                                          currency_unit,
                                                          -cost_per_year
                                                          )
            elif utility_name == "heat thermal":
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          heat_thermal_mass * self.production_time,
                                                          an_utility_info.unit,
                                                          an_utility_info.name,
                                                          an_utility_info.unit_cost,
                                                          currency_unit,
                                                          -heat_thermal_mass * an_utility_info.unit_cost
                                                          * self.production_time
                                                          )
            elif utility_name == "make up water":
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          make_up_water * self.production_time,
                                                          an_utility_info.unit,
                                                          an_utility_info.name,
                                                          an_utility_info.unit_cost,
                                                          currency_unit,
                                                          -make_up_water * an_utility_info.unit_cost
                                                          * self.production_time
                                                          )
            elif utility_name == "water treatment":
                self.__utility[obj_id] = ProcessComponent(obj_id,
                                                          None,
                                                          water_treatment * self.production_time,
                                                          an_utility_info.unit,
                                                          an_utility_info.name,
                                                          an_utility_info.unit_cost,
                                                           currency_unit,
                                                          -water_treatment * an_utility_info.unit_cost
                                                          * self.production_time
                                                          )
            else:
                print("[Warning:] Unknown ", utility_name)
        return True

    def update_process_line(self, contents, product_chemical_id, all_utility_info, all_chem_info, emission_data):
        """       
        update the whole process's products, byproducts, materials, utilities, emissions
        :param contents
        :param product_chemical_id: id of the chemical whose quantity or other attributes have been changed
        :param all_utility_info: dictionary of utility_type info
        :param all_chem_info: 
        :param emission_data: emission data for a specific reaction_formula
        :return: 
        """
        # update the process info
        self.days_of_production = contents['DOP']
        self.hours_of_production = contents['HOP']
        self.conversion = contents['conversion']
        if product_chemical_id not in self.__products:
            return [False, "unknown product_id " + product_chemical_id + " in reaction_formula " + self.rf_name]
        a_product = self.__products[product_chemical_id]
        # 1. update product quantity
        ratio = 1.0 * contents['quantity'] / a_product.quantity
        a_product.quantity = contents['quantity']
        # 2. update product value
        new_value_per_unit = contents['value_per_unit_' + str(product_chemical_id)]
        # update the local price: the price of the component will not affect other factory having the component
        a_product.value_per_unit = new_value_per_unit
        a_product.calculate_product_value(all_chem_info[product_chemical_id], new_value_per_unit)
        # updates also other products of this production line!
        for chem_id, other_product in self.__products.items():
            if chem_id != product_chemical_id:
                # update quantity
                other_product.quantity = other_product.quantity * ratio
                # update value per unit, both in the Chemical and ProcessProduct
                new_value_per_unit = contents['value_per_unit_' + str(chem_id)]
                other_product.value_per_unit = new_value_per_unit
                # recalculate the product value
                other_product.calculate_product_value(all_chem_info[chem_id], new_value_per_unit)

        # 3. update material consumption
        succeed = a_product.calculate_materials(self.__ref_product.moles_per_second, self.__material, self.conversion,
                                                self.production_time, self.rf_info, all_chem_info, True)
        if not succeed: return [False, 'Failed to update material']
        # 4. update emission
        if emission_data is not None:
            succeed = self.calculate_process_emission(emission_data, True)
        if not succeed: return [False, 'Failed to update emission']
        # 5. update utilities consumption
        succeed = self.calculate_process_utilities(all_utility_info, all_chem_info)
        if not succeed: return [False, 'Failed to update utility']
        # 6. update byproducts
        succeed = self.calculate_byproducts(all_chem_info, True)[1]
        if not succeed: return [False, 'Failed to update byproducts']
        return [True]

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
        return -(sum(v.annual_value for v in self.__material.values()))

    @property
    def byproducts_cost(self):
        """
        :return: cost all byproducts of the process
        """
        return -(sum(v.annual_value for v in self.__byproducts.values()))

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
        revenue = self.products_value - self.material_cost - self.byproducts_cost - self.utilities_cost
        # convert the revenue
        value_unit = self.__ref_product.currency
        return round(UnitConversion.convert(revenue, value_unit, MEGA+value_unit, "CURRENCY"), NUM_DIGITS), MEGA+value_unit

    @property
    def utilities_cost(self):
        """
        :return: cost of all utilities
        """
        return -sum(u.annual_value for u in self.__utility.values())

    @property
    def factory_process_json(self):
        """
        :return: dictionary of factory process information
        """
        return {'rf_name': self.rf_name,
                'process_basis': {'DOP': self.days_of_production, 'HOP': self.hours_of_production,
                                  'inlet_T': self.inlet_temperature, 'inlet_P': self.inlet_pressure,
                                  'conversion': self.conversion},
                'products': [p.component_json for p in self.__products.values()],
                'by_products': [p.component_json for p in self.__byproducts.values()],
                'material': [p.component_json for p in self.__material.values()],
                'emissions': [p.component_json for p in self.__emission.values()],
                'utilities': [p.component_json for p in self.__utility.values()],
                'process_annual_revenue': self.revenue_per_year[0],
                'revenue_unit': self.revenue_per_year[1]
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
        new_product_line = False
        if rf_id not in self.__product_lines:
            new_product_line = True
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
        # the product_line existed, this product need to added, but its quantity should be consistent with the reference
        # add the target product
        self.__product_lines[rf_id].add_product(product_chem_id,
                                                quantity,
                                                quantity_unit,
                                                chemicals_info,
                                                new_product_line
                                                )

    def calculate_byproducts_per_product_line(self, chemicals_info):
        """
        calculate byproducts per product line in the factory, call this function only AFTER all the products
        of the product line is calculated
        :param chemicals_info:
        :return:
        """
        for rf_id, product_line in self.factory_product_lines.items():
            list_byproducts = product_line.calculate_byproducts(chemicals_info)[0]
            print(list_byproducts, " byproducts are added for ", product_line.rf_info.name, ' for ', self.factory_name)

    def calculate_emission_per_product_line(self, all_emission_data):
        for rf_id, product_line in self.__product_lines.items():
            # check whether there are emission data for this reaction formula
            if rf_id in all_emission_data:
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
        store the utilities types that a process is used by the factory, no calculation yet
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
        sum of revenue per product line
        :return: total revenue of the factory
        """
        rt_value = 0
        value_unit = ""
        for product_line in self.__product_lines.values():
            rt_value += product_line.revenue_per_year[0]
            value_unit = product_line.revenue_per_year[1]
        return rt_value, value_unit

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
        """
        :return: all the factory product processes
        """
        results = {'total_profit': self.factory_revenue[0],
                   'profit_unit': self.factory_revenue[1],
                   'product_lines': []
                  }
        for rf_id, product in self.__product_lines.items():
            results['product_lines'].append((rf_id, product.factory_process_json))
        return results
