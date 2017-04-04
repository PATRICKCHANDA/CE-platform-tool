class RFComponent:
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


class RFProduct(RFComponent):
    """
    represent reaction formula product
    """
    def __init__(self, info):
        RFComponent.__init__(self, info)
        self.quantity = info.GetField('quantity')


class RFReactant(RFComponent):
    """
    represent reaction formula reactant
    """
    def __init__(self, info):
        RFComponent.__init__(self, info)
        # it is a formula to calculate # of moles in order to product 1 moles product
        self.quantity_ratio = info.GetField('quantity')
        self.__prev_reaction_formula_id = info.GetField('prev_reaction_formula_id')
        if info.GetField('catalyst') is None or info.GetField('catalyst') == False:
            self.is_catalyst = False
        else:
            self.is_catalyst = True


class ReactionFormula:
    """
    represent the reaction formula: reaction conditions, conversion, and its reactant(s)
    """
    def __init__(self, info, is_product):
        self.name = info.GetField('description')
        self.temperature = info.GetField('temperature')
        self.pressure = info.GetField('pressure')
        self.heat_reaction_formula = info.GetField('heat_reaction')
        self.__reactants = {}
        self.__products = {}
        self.add_reaction_component(info, is_product)

    @property
    def reactants(self):
        return self.__reactants

    @property
    def products(self):
        return self.__products

    def add_reaction_component(self, info, is_product):
        chemical_id = info.GetField('chemical_id')
        if is_product:
            self.__products[chemical_id] = RFProduct(info)
        else:
            self.__reactants[chemical_id] = RFReactant(info)

    @property
    def json_format(self):
        return {"name": self.name,
                "temperature": self.temperature,
                "pressure": self.pressure,
                "reactants": [r.json_format for r in self.__reactants.values()],
                "products": [p.json_format for p in self.__products.values()]
                }
