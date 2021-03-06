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

    value > 0: factory produce/supply this item
    value < 0: factory use/recycle/treat this item
"""
from services.factory_data import Factory
import numpy as np
from collections import deque
import itertools

SHORT_NAME_CHEMICAL = 'c'
SHORT_NAME_UTILITY_TYPE = 'u'
SHORT_NAME_EMISSION = 'e'
SHORT_NAME_FACTORY = 'f'
DUMMY_FACTORY_ID = 1E8
CURT_DUMMY_FACTORY_ID = DUMMY_FACTORY_ID


class CEAnalysis:
    OFFSET_FACTORY = 0
    OFFSET_CHEMICAL = 10000000
    OFFSET_UTILITY_TYPE = 20000000
    OFFSET_EMISSION = 30000000
    PREFIX_EMISSION = 'emis_'

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
        # store the row_index : object_id + offset)
        self.dict_row_index_2_obj_id = dict()
        # store the col_index: object_id + offset)
        self.dict_col_index_2_obj_id = dict()

        # row: factory
        row_index = itertools.count(0)
        for factory_obj_id in all_factory.keys():
            unique_factory_id = CEAnalysis.__generate_unique_obj_id(factory_obj_id, SHORT_NAME_FACTORY)
            index = next(row_index)
            self.dict_obj_id_2_index[unique_factory_id] = index
            self.dict_row_index_2_obj_id[index] = unique_factory_id

        # column: chemicals
        col_index = itertools.count(0)
        for chem_obj_id in all_chemical.keys():
            unique_chem_id = CEAnalysis.__generate_unique_obj_id(chem_obj_id, SHORT_NAME_CHEMICAL)
            index = next(col_index)
            self.dict_obj_id_2_index[unique_chem_id] = index
            self.dict_col_index_2_obj_id[index] = unique_chem_id

        # column: utility types
        for utility_object_id in all_utility_type.keys():
            unique_utility_id = CEAnalysis.__generate_unique_obj_id(utility_object_id, SHORT_NAME_UTILITY_TYPE)
            index = next(col_index)
            self.dict_obj_id_2_index[unique_utility_id] = index
            self.dict_col_index_2_obj_id[index] = unique_utility_id

        # column: emissions, use emission name, not the object_id, since different object_id may point to the same
        # emission. The emission data is per reaction_formula related
        for emission_per_rf in all_emission.values():
            for emission_data in emission_per_rf:
                emission_name = CEAnalysis.__generate_unique_obj_id(emission_data.name, SHORT_NAME_EMISSION)
                if emission_name not in self.dict_obj_id_2_index:
                    index = next(col_index)
                    self.dict_obj_id_2_index[emission_name] = index
                    self.dict_col_index_2_obj_id[index] = emission_name

        n_rows = len(self.dict_row_index_2_obj_id)
        n_cols = len(self.dict_col_index_2_obj_id)
        assert(n_rows + n_cols == len(self.dict_obj_id_2_index))
        # create the 2D array and make a copy
        self.A = np.zeros((n_rows, n_cols), dtype=np.float64)
        self.__A = self.A.copy()
        # get the total margin and make a copy
        self.total_margin = self.calc_total_margin(all_factory)
        self.__prev_total_margin = list(self.total_margin)

    def append_new_factory(self, factory_id):
        row_index, num_cols = self.A.shape
        unique_factory_id = CEAnalysis.__generate_unique_obj_id(factory_id, SHORT_NAME_FACTORY)
        # save the index
        self.dict_obj_id_2_index[unique_factory_id] = row_index
        self.dict_row_index_2_obj_id[row_index] = unique_factory_id
        # append the new row
        new_row = [[0 for i in range(num_cols)]]
        self.A = np.append(self.A, new_row, axis=0)

    def calc_total_margin(self, all_factories):
        total_revenue = 0
        unit = ""
        for factory in all_factories.values():
            total_revenue += factory.factory_revenue[0]
            if factory.factory_revenue[1] != '':
                unit = factory.factory_revenue[1]
        return [total_revenue, unit]

    def get_factory_id_by_index(self, row_index):
        """
        get the factory_id on the items defined in the row 
        :param row_index: 
        :return: 
        """
        object_id = self.dict_row_index_2_obj_id.get(row_index) - CEAnalysis.OFFSET_FACTORY
        return object_id

    def get_object_id_by_index(self, col_index):
        """     
          get the items object_id on the items defined in the column
        :param col_index: column index of the 2D array
        :return: object_id from the database, which is used as dictionary key in their container respectively
        """
        object_id = self.dict_col_index_2_obj_id.get(col_index)
        if type(object_id) is int:
            if CEAnalysis.OFFSET_CHEMICAL < object_id < CEAnalysis.OFFSET_UTILITY_TYPE:
                return object_id - CEAnalysis.OFFSET_CHEMICAL, SHORT_NAME_CHEMICAL
            elif CEAnalysis.OFFSET_UTILITY_TYPE < object_id < CEAnalysis.OFFSET_EMISSION:
                return object_id - CEAnalysis.OFFSET_UTILITY_TYPE, SHORT_NAME_UTILITY_TYPE
        else:
            # since the column name for emission starts with 'emis_', so we return a substring of the column name
            return object_id[5:], SHORT_NAME_EMISSION

    @staticmethod
    def __generate_unique_obj_id(object_id, name):
        """       
        :param object_id: id or name if it is emission 
        :param name: 
        :return: 
        """
        unique_obj_id = object_id
        if name.lower() == SHORT_NAME_CHEMICAL:
            unique_obj_id = CEAnalysis.OFFSET_CHEMICAL + int(object_id)
        elif name.lower() == SHORT_NAME_FACTORY:
            unique_obj_id = CEAnalysis.OFFSET_FACTORY + int(object_id)
        elif name.lower() == SHORT_NAME_UTILITY_TYPE:
            unique_obj_id = CEAnalysis.OFFSET_UTILITY_TYPE + int(object_id)
        elif name.lower() == SHORT_NAME_EMISSION:
            unique_obj_id = CEAnalysis.PREFIX_EMISSION + object_id
        else:
            print("[Warning]: unknown name", name)
            raise ValueError("Unknown name to generate the column index")
        return unique_obj_id

    def get_index_by_id(self, object_id, name):
        """
        :param object_id: object_id or name(of emission) of the item from database
        :param name: indication of factory, emission ,utility and chemical
        :return: index of one axis of the 2D array 
        """
        unique_obj_id = CEAnalysis.__generate_unique_obj_id(object_id, name)
        # for emission, the object_id is actually the emission name, not an integer
        index = self.dict_obj_id_2_index.get(unique_obj_id)
        if index is None:
            raise ValueError("[Error]: no index found for " + str(unique_obj_id))
        return index

    def get_factory_ids_by_col_id(self, col_object_id, item_type_name, larger_than_zero):
        """
        with a known col_object_id, indicating as a chemical, emis, utility, return a list of factory id's
        :param col_object_id: 
        :param item_type_name: 
        :return: a list of factory_id which produce/supply the chemical or service indicated by the col_object_id
        """
        col_index = self.get_index_by_id(col_object_id, item_type_name)
        # in the array column, get all the entries whose value > 0, which means the factory produce/supply
        # this product or service
        a_column = self.A[:, col_index]
        if larger_than_zero:
            row_indices = np.where(a_column > 0)
        else:
            row_indices = np.where(a_column < 0)
        if len(row_indices[0]) > 0:
            factory_ids = [self.get_factory_id_by_index(i.item(0)) for i in np.nditer(row_indices[0])]
            return factory_ids
        else:
            return []

    def set_value(self, factory_obj_id, col_object_id, name, value, plus):
        """       
        :param factory_obj_id: 
        :param col_object_id:  object_id of emission, utility or chemical
        :param name: indication of e(emission), u(utility) or c(chemical)
        :param value: 
        :param plus: boolean, if True, use +=, otherwise use -=, which will substract the info from the array
        :return: 
        """
        row_index = self.get_index_by_id(factory_obj_id, SHORT_NAME_FACTORY)
        col_index = self.get_index_by_id(col_object_id, name)
        if plus:
            self.A[row_index, col_index] += value
        else:
            self.A[row_index, col_index] -= value

    def process_factory_product_line_info(self, factory_id, product_line, plus=True):
        info = product_line.factory_process_json
        # factory products
        for product in info['products']:
            # get product object_id
            self.set_value(factory_id, product['id'], SHORT_NAME_CHEMICAL, product['quantity'], plus)
        # by-products
        for byproduct in info['by_products']:
            self.set_value(factory_id, byproduct['id'], SHORT_NAME_CHEMICAL, byproduct['quantity'], plus)
        # material
        for material in info['material']:
            self.set_value(factory_id, material['id'], SHORT_NAME_CHEMICAL, -material['quantity'], plus)
        # utilities
        for utility in info['utilities']:
            self.set_value(factory_id, utility['id'], SHORT_NAME_UTILITY_TYPE, -utility['quantity'], plus)
        # todo: factory may also provide utility services, data model necessary
        # emissions
        for emission in info['emissions']:
            self.set_value(factory_id, emission['name'], SHORT_NAME_EMISSION, emission['quantity'], plus)

    def process_factory_information(self, factory_id, factory, plus=True):
        # process each product_line
        for rf_id, product_line in factory.factory_product_lines.items():
            self.process_factory_product_line_info(factory_id, product_line, plus)

    def process_all_factories_information(self, factories, plus=True):
        # fill in the data
        # add per factory
        for factory_id, factory in factories.items():
            # add per factory
            self.process_factory_information(factory_id, factory, plus)

    def calc_total_quantity_per_item(self):
        # # sum on each column original  __A
        # sum_ori = self.__A.sum(axis=0)
        # # sum on each column current A
        # sum_curt = self.A.sum(axis=0)
        return self.A.sum(axis=0)

    def compare_begin(self):
        self.__A = self.A.copy()
        self.__prev_total_margin = list(self.total_margin)

    def compare(self, all_chemical, all_utility_type, all_factory):
        """
        compare the update array with the original array 
        :return: a dictionary of {item_name: (num before change, num after change), ......}
        """
        # sum on each column original  __A
        sum_ori = self.__A.sum(axis=0)
        # sum on each column current A
        sum_curt = self.A.sum(axis=0)
        # get the non-zero elements' location
        diff_idx = np.where((sum_curt - sum_ori) != 0)
        result = {}
        for i in diff_idx[0]:
            item = self.get_object_id_by_index(i)
            item_name = item[1]
            # todo: get the unit (confirm for the emission)
            if item_name == SHORT_NAME_CHEMICAL:
                item_name = all_chemical[item[0]].name + "(" + all_chemical[item[0]].unit + ")"
            elif item_name == SHORT_NAME_UTILITY_TYPE:
                item_name = all_utility_type[item[0]].name + "(" + all_utility_type[item[0]].unit + ")"
            elif item_name == SHORT_NAME_EMISSION:
                item_name = item[0] + "(T)"
            result[item_name] = ((sum_ori[i]), (sum_curt[i]), sum_curt[i]-sum_ori[i])

        self.total_margin = self.calc_total_margin(all_factory)
        key_name = 'Total Margin(' + self.total_margin[1] + ')'
        result[key_name] = (self.__prev_total_margin[0], self.total_margin[0], self.total_margin[0] - self.__prev_total_margin[0])
        return result

    def remove_factory_contribution(self, factory_ids):
        if len(factory_ids) > 0:
            row_indices = [self.get_index_by_id(i, SHORT_NAME_FACTORY) for i in factory_ids]
            self.A = np.delete(self.A, row_indices, axis=0)
            # remove from the container
            for i in factory_ids:
                del self.dict_obj_id_2_index[i]
            for i in row_indices:
                del self.dict_row_index_2_obj_id[i]

    @property
    def json_format(self):
        return {'id2idx': self.dict_obj_id_2_index,
                'rIdx2id': self.dict_row_index_2_obj_id,
                'cIdx2id': self.dict_col_index_2_obj_id
                }


def traverse_to_upstream_process(analyzer,
                                 queue_items,
                                 factories,
                                 curt_factory_id,
                                 curt_rf_id,
                                 all_emission_data,
                                 all_utility_info,
                                 all_chemicals,
                                 all_reactions
                                 ):
    """
    calculate the emission,consumption, etc. of the current reaction, then calculate that of its upstream process, until
    there are no more upstream process
    :param analyzer: 
    :param queue_items: initial process information {rf_id : (factory_ids, data)}, data here is the production related parameters
    :param factories: 
    :param curt_factory_id: 
    :param curt_rf_id: 
    :param all_emission_data: 
    :param all_utility_info: 
    :param all_chemicals: 
    :param all_reactions: 
    :return: 
    """
    global CURT_DUMMY_FACTORY_ID
    queue_rf_id = deque([])
    queue_rf_id.extend(queue_items)
    # # get current quantity
    # curt_product_id = post_data['desired_chemical_id']
    # if curt_factory_id in factories:
    #     curt_quantity = factories[curt_factory_id].factory_product_lines[curt_rf_id].products[curt_product_id].quantity
    # else:
    #     curt_quantity = 0
    # # if post_data['quantity'] != curt_quantity:
    # # calc and save extra quantity: because if there are factories bond with process, need to UPDATE the total quantity
    # post_data['desired_quantity'] = post_data['desired_quantity'] - curt_quantity  # >0:increase;  <0: decrease
    # # initial the queue, which is the current process
    # queue_rf_id = deque([{curt_rf_id: ([curt_factory_id], post_data)}])

    # analyzer.compare_begin()
    counter = 0
    while len(queue_rf_id) > 0:
        counter += 1
        # popup a reaction formula, and its related data
        an_item = queue_rf_id.popleft()
        rf_id, detail = next(iter(an_item.items()))
        factory_ids, feature = detail
        product_id = feature['desired_chemical_id']
        # extra_quantity = feature['quantity']
        # get the factory id,
        # for an upstream process, there could be more than one factory produce the same product, but we assign
        # the new volume only to 1 factory
        if factory_ids is not None:
            factory_id = factory_ids[0]
            # 1. get the product-line detail of this factory
            a_productline = factories[factory_id].factory_product_lines[rf_id]
            # remove emission, consumption from the analyzer
            analyzer.process_factory_product_line_info(factory_id, a_productline, False)
            # update the current quantity of this product in this factory
            feature['desired_quantity'] += a_productline.products[product_id].quantity
            # 2. update the specific product_line of this factory
            if rf_id in all_emission_data:
                results = a_productline.update_process_line(feature, product_id, all_utility_info, all_chemicals, all_emission_data[rf_id])
                if not results[0]:
                    return results
            else:
                results = a_productline.update_process_line(feature, product_id, all_utility_info, all_chemicals, None)
                if not results[0]:
                    return results
            # 3. update the CE_analyzer: ADD the info into the CE_analyzer
            analyzer.process_factory_product_line_info(factory_id, a_productline, True)
        else:  # if no factories are bond with the process, create dummy factory
            # make a dummy factory
            new_factory_id = CURT_DUMMY_FACTORY_ID + counter
            dummy_factory_info = {"id": new_factory_id,
                                  'properties': {'name': 'dummy', 'category': 'petrochemical'},
                                  'geometry': None
                                  }
            dummy_factory = Factory(dummy_factory_info)
            # add a product line
            dummy_factory.add_product_line(feature, rf_id, all_reactions, all_chemicals)
            dummy_factory.calculate_byproducts_per_product_line(all_chemicals)
            dummy_factory.calculate_emission_per_product_line(all_emission_data)
            dummy_factory.calculate_utilities_per_product_line(all_utility_info, all_chemicals)
            # save the factory
            factories[new_factory_id] = dummy_factory
            # save the factory id into all reactions
            all_reactions[rf_id].add_factory_id(new_factory_id)
            # increase one row in the array in the Analyzer
            analyzer.append_new_factory(new_factory_id)
            analyzer.process_factory_product_line_info(new_factory_id, dummy_factory.factory_product_lines[rf_id], True)

        # 4. calculate the volume difference of all related item after calculating this process, the quantity difference
        # is part of the data for the upstream process
        quantity_per_item = analyzer.calc_total_quantity_per_item()
        new_entries = prepare_upstream_process(all_reactions, analyzer, quantity_per_item, rf_id)
        queue_rf_id.extend(new_entries)

    # save the current max dummy factory id, in case of next time use
    CURT_DUMMY_FACTORY_ID += counter

    # 4. final compare to return the results
    return [True, "whole process chain updating is succeed"]


def prepare_upstream_process(all_reactions, analyzer, quantity_per_comp, rf_id):
    results = []
    # identify all the input material, make sure the upstream process does produce the input material
    list_input = all_reactions[rf_id].reactants.keys()
    # get the upstream process id of the current reaction formula, and also the output of upstream process
    for upstream_rf_id in (all_reactions[rf_id].upstream_process_ids or []):
        list_output_upstream_process = all_reactions[upstream_rf_id].products.keys()
        # find which input(s) of current process are supplied by the the upstream process
        common_product_ids = set(list_output_upstream_process).intersection(set(list_input))
        if common_product_ids is None:
            continue
        # if more than 1 inputs are supplied, we only need to specify 1 of them,
        # the others will be handled in calculation
        a_product_id = common_product_ids.pop()
        # get the volume of this product that needs to be produced by this upstream process
        col_index = analyzer.get_index_by_id(a_product_id, SHORT_NAME_CHEMICAL)
        quantity = quantity_per_comp[col_index]
        #    quantity > 0: we have enough of the product after changing the capacity of DOWNSTREAM process, do nothing!
        if quantity > 0:
            continue
        # if quantity < 0, we are lacking of the product, need to produce more!
        if all_reactions[upstream_rf_id].list_factories is not None:
            # there are factories, we do update on the factory, we setup the content like this:
            tmp = {"desired_chemical_id": a_product_id,
                   "desired_quantity": -quantity
                   }
        else:
            # extra_quantity > 0 --> decrease the production, however, there is no factory(even no dummy factory)
            # linked with this process, but we will create dummy factory to produce the product

            # there are no actual factories for this process, we will create factory, so we setup content like this
            tmp = {"desired_chemical_id": a_product_id,
                   # always make it positive, since dummy factory need to produce
                   "desired_quantity": abs(quantity),
                   "unit": 'T',
                   "days_of_production": 340,
                   "hours_of_production": 24,
                   "inlet_temperature": 20,
                   "inlet_pressure": 1,
                   "level_reactions": -1,
                   "conversion": all_reactions[rf_id].default_conversion,
                   "percent_heat_removed": 0.02
                   }
        # push upstream process in the queue
        results.append({upstream_rf_id: (all_reactions[upstream_rf_id].list_factories, tmp)})
    return results


def remove_dummy_factory(factories, analyzer):
    global CURT_DUMMY_FACTORY_ID
    # get list of key whose value > DUMMY_FACTORY_ID
    factory_ids = [i for i in factories.keys() if i > DUMMY_FACTORY_ID]
    analyzer.remove_factory_contribution(factory_ids)
    for i in (factory_ids or []):
        del factories[i]
    # reset
    CURT_DUMMY_FACTORY_ID = DUMMY_FACTORY_ID
