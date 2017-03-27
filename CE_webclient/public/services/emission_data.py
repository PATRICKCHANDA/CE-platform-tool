class EmissionData:
    """
    represent public.emission_data
    """
    def __init__(self, info):
        self.__id = info.GetField('object_id')
        self.__name_en = info.GetField('name_en')
        self.__name_cn = info.GetField('name_cn')
        self.unit = info.GetField('unit')   # kg/kg
        self.__process = info.GetField('process')
        self.__heat = info.GetField('heat')
        self.__electricity = info.GetField('electricity')
        self.total = info.GetField('total')

    @property
    def name(self):
        return self.__name_cn + "(" + self.__name_en + ")"
