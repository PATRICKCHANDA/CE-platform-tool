class Chemical:
    """
    information from public.chemical table
    """
    def __init__(self, info):
        """
        :param info: dictionary (json format)
        """
        tmp = info['properties']
        self.__name_cn = tmp['name_cn']
        self.__name_en = tmp['name_en']
        self.molar_mass = tmp['molar_mass']
        self.density = tmp['density']
        self.symbol = tmp['symbol']
        self.unit = tmp['unit']
        self.unit_cost = tmp['unit_cost']   # cost per 'unit'
        self.unit_transport_cost = tmp['unit_transport_cost']
        self.currency = tmp['cost_currency']
        self.sp_heat = tmp['sp_heat']   # unit: J/Kg.K at STP(standard temperature pressure)

    @property
    def name(self):
        return self.__name_cn + "(" + self.__name_en + ")"

    @property
    def json_format(self):
        return {"name": self.name,
                "name_en":self.__name_en,
                "name_cn": self.__name_cn,
                "molar_mass": self.molar_mass,
                "density": self.density,
                "symbol": self.symbol,
                "unit": self.unit,
                "value_per_unit": self.unit_cost,
                "unit_transport_cost": self.unit_transport_cost,
                "currency": self.currency,
                "sp_heat": self.sp_heat
                }