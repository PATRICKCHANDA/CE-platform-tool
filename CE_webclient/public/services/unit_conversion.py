class UnitConversion:
    """
    provides unit conversion functionality
    """
    QUALITY = 'QUALITY'
    TIME = 'TIME'
    LinearConversionTable = dict()
    LinearConversionTable[QUALITY] = dict()
    LinearConversionTable[TIME] = dict()

    LinearConversionTable[QUALITY]['g'] = 1
    LinearConversionTable[QUALITY]['kg'] = 1E3
    LinearConversionTable[QUALITY]['t'] = 1E6
    LinearConversionTable[TIME]["s"] = 1
    LinearConversionTable[TIME]["m"] = 60
    LinearConversionTable[TIME]["min"] = 60
    LinearConversionTable[TIME]["mins"] = 60
    LinearConversionTable[TIME]["h"] = 60 * 60
    LinearConversionTable[TIME]["hr"] = 60 * 60
    LinearConversionTable[TIME]["hrs"] = 60 * 60
    LinearConversionTable[TIME]["d"] = 24 * 60 * 60
    LinearConversionTable[TIME]["day"] = 24 * 60 * 60
    LinearConversionTable[TIME]["days"] = 24 * 60 * 60
    LinearConversionTable[TIME]["y"] = 365.25 * 24 * 60 * 60
    LinearConversionTable[TIME]["year"] = 365.25 * 24 * 60 * 60
    LinearConversionTable[TIME]["years"] = 365.25 * 24 * 60 * 60

    @classmethod
    def convert(cls, value, src_unit, dst_unit, quantity):
        """
        unit conversion on quality
        :param value: float
        :param src_unit: str
        :param dst_unit: str
        :param quantity: str
        :return: converted value in dst_unit
        """
        # make case insensitive
        src_unit = src_unit.lower().strip()
        dst_unit = dst_unit.lower().strip()
        quantity = quantity.upper()

        if src_unit in cls.LinearConversionTable[quantity] \
                and dst_unit in cls.LinearConversionTable[quantity]:
            return value * cls.LinearConversionTable[quantity][src_unit] / \
                   cls.LinearConversionTable[quantity][dst_unit]
        else:
            return float('NaN')
