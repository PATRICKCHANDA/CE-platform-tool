class Reactant:
    def __init__(self, info):
        if __debug__:
            self.chemical_id = info.GetField('chemical_id')
        self.reaction_formula_id = info.GetField('reaction_formula_id')
        # it is a formula to calculate # of moles in order to product 1 moles product
        self.quantity_ratio = info.GetField('quantity')
        # default should be moles
        self.unit = info.GetField('unit')
        if self.unit != 'moles':
            print("[WARNING]: unit in reaction_reactant table should be moles. Further calculation will use moles!")
        self.__prev_reaction_formula_id = info.GetField('prev_reaction_formula_id')


class ReactionFormula:
    """
    represent the reaction formula: reaction conditions, conversion, and its reactant(s)
    """
    def __init__(self, info):
        self.__name_en = info.GetField('name_en')
        self.__name_cn = info.GetField('name_cn')
        self.temperature = info.GetField('temperature')
        self.pressure = info.GetField('pressure')
        self.__reactants = {}
        self.add_reactant(info)

    @property
    def name(self):
        return self.__name_cn + "(" + self.__name_en + ")"

    @property
    def reactants(self):
        return self.__reactants

    def add_reactant(self, info):
        chemical_id = info.GetField('chemical_id')
        self.__reactants[chemical_id] = Reactant(info)
