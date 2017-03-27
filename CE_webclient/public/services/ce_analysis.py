"""
    analyze the relationship among factories, infrastructures with all the chemicals, emissions, utilities

    generate a 2D array:
             | chem1 chem2 chem3 chem4 emis1 emis2 utility1 ......
    ---------|---------------------------------------
    factory1 |   10
    factory2 |   -15
    factory3 |
    infra1   |
    infra2   |

    value > 0: factory produce/generate this item
    value < 0: factory use/recycle/treat this item
"""
import numpy as np
import itertools


class CEAnalysis:
    OFFSET_FACTORY = 0
    OFFSET_CHEMICAL = 10000000
    OFFSET_UTILITY_TYPE = 20000000
    OFFSET_EMISSION = 30000000

    def __init__(self, all_factory, all_chemical, all_utility_type, all_emission):
        """
            create a dictionary to use their DB object_id + unique_offset as key, and internal increased Index as value
            and another dictionary to store the reversed (key,value) of the previous dictionary
        :param all_factory:
        :param all_chemical:
        :param all_utility_type:
        :param all_emission: {rf_id: EmissionData}
        :return:
        """
        # all the object_id + offset : internal index
        self.dict_obj_id_2_index = dict()
        # store the row_index : object_id (no offset)
        self.dict_row_index_2_obj_id = dict()
        # store the col_index: object_id (no offset)
        self.dict_col_index_2_obj_id = dict()

        # row: factory
        row_index = itertools.count(0)
        for factory_obj_id in all_factory.keys():
            unique_factory_id = CEAnalysis.OFFSET_FACTORY + factory_obj_id
            index = next(row_index)
            self.dict_obj_id_2_index[unique_factory_id] = index
            self.dict_row_index_2_obj_id[index] = unique_factory_id

        # column: chemicals
        col_index = itertools.count(0)
        for chem_obj_id in all_chemical.keys():
            unique_chem_id = CEAnalysis.OFFSET_CHEMICAL + chem_obj_id
            index = next(col_index)
            self.dict_obj_id_2_index[unique_chem_id] = index
            self.dict_col_index_2_obj_id[index] = unique_chem_id

        # column: utility types
        for utility_object_id in all_utility_type.keys():
            unique_utility_id = CEAnalysis.OFFSET_UTILITY_TYPE + utility_object_id
            index = next(col_index)
            self.dict_obj_id_2_index[unique_utility_id] = index
            self.dict_col_index_2_obj_id[index] = unique_utility_id

        # column: emissions, use emission name, not the object_id, since different object_id may point to the same
        # emission
        for emission_per_rf in all_emission.values():
            for emission_data in emission_per_rf:
                emission_name = 'emis_' + emission_data.name
                if emission_name not in self.dict_obj_id_2_index:
                    index = next(col_index)
                    self.dict_obj_id_2_index[emission_name] = index
                    self.dict_col_index_2_obj_id[index] = emission_name

        n_rows = len(self.dict_row_index_2_obj_id)
        n_cols = len(self.dict_col_index_2_obj_id)
        assert(n_rows + n_cols == len(self.dict_obj_id_2_index))
        # create the 2D array
        self.A = np.zeros((n_rows, n_cols), dtype=np.float64)

    def get_factory_id_by_index(self, index):
        object_id = self.dict_row_index_2_obj_id.get(index)
        return object_id

    def get_object_id_by_index(self, index):
        """       
        :param index: column index of the 2D array
        :param name: 'f' for factory, 'e' for emission, 'c' for chemical, 'u' for utility
        :return: object_id from the database, which is used as dictionary key in their container respectively
        """
        object_id = self.dict_col_index_2_obj_id.get(index)
        if type(object_id) is int:
            if CEAnalysis.OFFSET_CHEMICAL < object_id < CEAnalysis.OFFSET_UTILITY_TYPE:
                return object_id, 'c'
            elif CEAnalysis.OFFSET_UTILITY_TYPE < object_id < CEAnalysis.OFFSET_EMISSION:
                return object_id, 'u'
        else:
            return object_id[5:], 'e'

    def get_index_by_id(self, object_id, name):
        """
        :param object_id: object_id or name(of emission) of the component from database
        :param name: indication of factory, emission ,utility and chemical
        :return: index of one axis of the 2D array 
        """
        unique_obj_id = object_id
        if name.lower() == "c":
            unique_obj_id += CEAnalysis.OFFSET_CHEMICAL
        elif name.lower() == "f":
            unique_obj_id += CEAnalysis.OFFSET_FACTORY
        elif name.lower() == "u":
            unique_obj_id += CEAnalysis.OFFSET_UTILITY_TYPE
        elif name.lower() == "e":
            unique_obj_id = 'emis_' + object_id
        else:
            print("[Warning]: unknown name", name)
            return None
        # for emission, the object_id is actually the emission name, not an integer
        index = self.dict_obj_id_2_index.get(unique_obj_id)
        if index is None:
            print("[Warning]: no index found for ", unique_obj_id)
        return index

    def set_value(self, factory_obj_id, col_object_id, name, value):
        """       
        :param factory_obj_id: 
        :param col_object_id:  object_id of emission, utility or chemical
        :param name: indication of e(emission), u(utility) or c(chemical)
        :param value: 
        :return: 
        """
        row_index = self.get_index_by_id(factory_obj_id, 'f')
        col_index = self.get_index_by_id(col_object_id, name)
        self.A[row_index, col_index] += value


