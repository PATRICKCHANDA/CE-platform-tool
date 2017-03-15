class UtilityType:
    """
    represent gaolanport.utility_type
    """
    def __init__(self, info):
        """
        :param info: OGRFeature
        """
        self.__name_en = info.GetField('name_en')
        self.__name_cn = info.GetField('name_cn')
        self.unit = info.GetField('unit')
        self.unit_cost = info.GetField('unit_cost')
        self.cost_currency = info.GetField('cost_currency')

    @property
    def name_en(self):
        return self.__name_en

    @property
    def name(self):
        return self.__name_cn + "(" + self.__name_en + ")"
