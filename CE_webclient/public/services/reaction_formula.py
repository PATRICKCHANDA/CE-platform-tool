class RFCompound:
    def __init__(self, info):
        self.chemical_id = info.GetField('chemical_id')
        self.reaction_formula_id = info.GetField('reaction_formula_id')
        self.unit = info.GetField('unit')
        if self.unit != 'moles':
            print("[WARNING]: unit in reaction_reactant table should be moles. Further calculation will use moles!")

    @property
    def json_format(self):
        return {"chem_id": self.chemical_id,
                "unit": self.unit
                }


class RFProduct(RFCompound):
    """
    represent reaction formula product
    """
    def __init__(self, info):
        RFCompound.__init__(self, info)
        self.quantity = info.GetField('quantity')
        self.is_byproduct = info.GetField('byproduct')


class RFReactant(RFCompound):
    """
    represent reaction formula reactant
    """
    def __init__(self, info):
        RFCompound.__init__(self, info)
        # it is a formula to calculate # of moles in order to product 1 moles product
        self.quantity_ratio = info.GetField('quantity')
        if info.GetField('catalyst') is None or info.GetField('catalyst') == False:
            self.is_catalyst = False
        else:
            self.is_catalyst = True


class ReactionFormula:
    """
    represent the reaction formula: reaction conditions, conversion, and its reactant(s)
    """
    def __init__(self, info, is_product):
        # reaction name
        self.name = info.GetField('description')
        # reaction conditions
        self.temperature = info.GetField('temperature')
        self.pressure = info.GetField('pressure')
        self.heat_reaction_formula = info.GetField('heat_reaction')
        self.default_conversion = info.GetField('default_conversion')

        # read the upstream formula ids
        temp_ids = info.GetField('upstream_formula_ids')
        self.__upstream_formula_ids = None
        if temp_ids:
            self.__upstream_formula_ids = info.GetField('upstream_formula_ids').split(",")
            self.__upstream_formula_ids = [int(i) for i in self.__upstream_formula_ids]
        # read the reactants and products
        self.__reactants = {}
        self.__products = {}
        self.add_reaction_compound(info, is_product)

        # setup the list of plants' ids using this reaction formula(process)
        self.__list_factories = []

    def add_factory_id(self, an_id):
        if an_id not in self.__list_factories:
            self.__list_factories.append(an_id)

    def add_reaction_compound(self, info, is_product):
        chemical_id = info.GetField('chemical_id')
        if is_product:
            self.__products[chemical_id] = RFProduct(info)
        else:
            self.__reactants[chemical_id] = RFReactant(info)

    def remove_factory_id(self, an_id):
        if an_id in self.__list_factories:
            self.__list_factories.remove(an_id)
        else:
            print(an_id, " does not exist in the list of process ", self.name)

    @property
    def reactants(self):
        return self.__reactants

    @property
    def products(self):
        return self.__products

    @property
    def list_factories(self):
        return self.__list_factories

    @property
    def json_format(self):
        return {"name": self.name,
                "temperature": self.temperature,
                "pressure": self.pressure,
                "reactants": [r.json_format for r in self.__reactants.values()],
                "products": [p.json_format for p in self.__products.values()]
                }

    @property
    def upstream_process_ids(self):
        return self.__upstream_formula_ids


