class Reactant:
    def __init__(self, info):
        if __debug__:
            self.chemical_id = info.GetField('chemical_id')
        self.reaction_formula_id = info.GetField('reaction_formula_id')
        self.quantity = info.GetField('quantity')
        self.unit = info.GetField('unit')
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
        self.conversion = info.GetField('conversion')
        self.__reactants = {}
        self.add_reactant(info)

    @property
    def name(self):
        return self.__name_cn + "(" + self.__name_en + ")"

    def add_reactant(self, info):
        chemical_id = info.GetField('chemical_id')
        self.__reactants[chemical_id] = Reactant(info)