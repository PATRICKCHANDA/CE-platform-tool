class UnitConversion:
    """
    provides unit conversion functionality
    """
    QUALITY = 'QUALITY'
    TIME = 'TIME'
    ENERGY = 'ENERGY'
    CURRENCY = "CURRENCY"
    LinearConversionTable = dict()
    LinearConversionTable[QUALITY] = dict()
    LinearConversionTable[TIME] = dict()
    LinearConversionTable[ENERGY] = dict()
    LinearConversionTable[CURRENCY] = dict()

    LinearConversionTable[CURRENCY]["eur"] = 1
    LinearConversionTable[CURRENCY]["rmb"] = 7
    LinearConversionTable[CURRENCY]["meur"] = 1E6

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

    LinearConversionTable[ENERGY]['j'] = 1.0  # joule
    LinearConversionTable[ENERGY]['kj'] = 1.0 * 1E3  # joule
    LinearConversionTable[ENERGY]['gj'] = 1.0 * 1E9  # joule
    LinearConversionTable[ENERGY]['kwh'] = 3.6 * 1E6

    @classmethod
    def convert(cls, value, src_unit, dst_unit, category):
        """
        unit conversion on quality
        :param value: float
        :param src_unit: str
        :param dst_unit: str
        :param category: str
        :return: converted value in dst_unit
        """
        # make case insensitive
        src_unit = src_unit.lower().strip()
        dst_unit = dst_unit.lower().strip()
        category = category.upper()

        if src_unit in cls.LinearConversionTable[category] \
                and dst_unit in cls.LinearConversionTable[category]:
            return value * cls.LinearConversionTable[category][src_unit] / \
                   cls.LinearConversionTable[category][dst_unit]
        else:
            return float('NaN')
