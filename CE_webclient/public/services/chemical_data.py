class Chemical:
    """
    public.chemical
    """
    def __init__(self, info):
        tmp = info['properties']
        self.__name_cn = tmp['name_cn']
        self.__name_en = tmp['name_en']
        self.molar_mass = tmp['molar_mass']
        self.density = tmp['density']
        self.symbol = tmp['symbol']
        self.unit = tmp['unit']
        self.unit_cost = tmp['unit_cost']
        self.unit_transport_cost = tmp['unit_transport_cost']
        self.description = tmp['description']

    @property
    def name(self):
        return self.__name_cn + "(" + self.__name_en + ")"