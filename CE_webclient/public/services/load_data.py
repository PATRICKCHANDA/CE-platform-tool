import sys
import json
from services.factory_data import Factory
from services.chemical_data import Chemical
from services.emission_data import EmissionData
from services.utility_type import UtilityType
from services.reaction_formula import ReactionFormula

try:
    from osgeo import osr, ogr, gdal
except ImportError(osr, ogr, gdal):
    sys.exit('Error: cannot find GDAL/OGR modules')


# enable GDAL/OGR exceptions
gdal.UseExceptions()


def get_all_drivers():
    """
    get all the drivers GDAL supports
    :return:
    """
    driver_dic = []
    cnt = ogr.GetDriverCount()
    for i in range(cnt):
        driver_name = ogr.GetDriver(i).GetName()
        if not driver_name in driver_dic:
            driver_dic.append(driver_name)
    print(driver_dic)


class DataLoader:
    """
    Postgres( with PostGIS extension) data loader
    """
    lyr_factory = 'gaolanport.factory'
    lyr_factory_reaction_product = 'gaolanport.factory_reaction_product'
    lyr_factory_reaction_utility = 'gaolanport.factory_reaction_utility'
    lyr_chemical = 'public.chemical'
    lyr_reaction_formula = 'public.reaction_formula'
    lyr_reaction_reactant = 'public.reaction_reactant'
    lyr_reaction_product = 'public.reaction_product'
    lyr_utility_type = "gaolanport.utility_type"
    lyr_emission_data = "public.emission_data"

    def __init__(self, db_server, db_name, db_user, db_pwd):
        """
        connect to postgres database
        :param db_server:
        :param db_name:
        :param db_user:
        :param db_pwd:
        """
        driver_name = 'PostgreSQL'
        drv = ogr.GetDriverByName(driver_name)
        self.__db_server = db_server
        self.__db_name = db_name
        self.conn = None
        if drv is None:
            print("%s driver not available.\n", driver_name)
            raise ValueError("No PostgreSQL driver is found. Unable to connect to database.\n")
        else:
            print(driver_name, " driver is available.\n")
            self.conn_str = "PG: host=%s dbname=%s user=%s password=%s" %(db_server, db_name, db_user, db_pwd)
            self.conn = ogr.Open(self.conn_str)
            if self.conn:
                print("[Info]: PostgreSQL database connected\n")

    def close(self):
        """
        close database connection
        :return:
        """
        print("[Info]: Database disconnected")
        self.conn = None

    def get_all_chemicals(self):
        """
        read the public.chemical table to get all the chemical information and save into a dictionary
        :return: {id: Chemical instance}
        """
        lyr = self.conn.GetLayer(DataLoader.lyr_chemical)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_chemical, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return None
        else:
            # print(lyr)
            if __debug__:
                feature_count = lyr.GetFeatureCount()
                print("# of chemicals: ", feature_count)
            rt_chemicals = {}
            for feature in lyr:
                feature_json = json.loads(feature.ExportToJson())
                obj_id = feature_json['id']
                rt_chemicals[obj_id] = Chemical(feature_json)
            # important: reset the reading
            lyr.ResetReading()
            return rt_chemicals

    def __get_reaction_formula_components(self, table_name, is_product, rt_reaction_formulas):
        """
        read public.reaction_formula & public.reaction_reactant or public.reaction_product
        :param table_name: reaction_product or reaction_reactant
        :param is_product: boolean, indicate product or reactant
        :param rt_reaction_formulas: dictionary of RF
        :return:
        """
        sql = 'SELECT a.*, b.* from ' + DataLoader.lyr_reaction_formula + ' a,' \
              + table_name + ' b ' \
              + 'WHERE a.object_id = b.reaction_formula_id'
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR SQL]: ", sql, self.__db_name, "@", self.__db_server)
            return None
        else:
            if __debug__:
                lyr_defn = lyr.GetLayerDefn()
                for i in range(lyr_defn.GetFieldCount()):
                    print(lyr_defn.GetFieldDefn(i).GetName())

            for feature in lyr:
                formula_id = feature.GetField('object_id')
                # create ReactionFormula if not exists in the container, otherwise updating the ReactionFormula
                if formula_id not in rt_reaction_formulas:
                    rt_reaction_formulas[formula_id] = ReactionFormula(feature, is_product)
                else:
                    rt_reaction_formulas[formula_id].add_reaction_component(feature, is_product)
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)

    def get_all_reaction_formulas(self):
        """
        get the reaction formula conditions, products and reactants
        :return: {id : ReactionFormula instance}
        """
        rt_reaction_formulas = dict()
        # add the reactants per reaction formula
        self.__get_reaction_formula_components(DataLoader.lyr_reaction_reactant, False, rt_reaction_formulas)
        # add the products per reaction formula
        self.__get_reaction_formula_components(DataLoader.lyr_reaction_product, True, rt_reaction_formulas)
        return rt_reaction_formulas

    def get_emission_data(self):
        """
        read the public.emission_data table information and save into a dictionary
        :return: {reaction_formula_id: list of EmissionData}
        """
        sql = "select * from " + DataLoader.lyr_emission_data
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_emission_data, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return None
        else:
            # print(lyr)
            if __debug__:
                feature_count = lyr.GetFeatureCount()
                print("# of emission data: ", feature_count)
            rt_emis_data = {}
            for feature in lyr:
                rf_id = feature.GetField('reaction_formula_id')
                if rf_id not in rt_emis_data:
                    rt_emis_data[rf_id] = [EmissionData(feature)]
                else:
                    rt_emis_data[rf_id].append(EmissionData(feature))
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)
            return rt_emis_data

    def get_factories(self):
        """
        read gaolanport.factory table to get factory information including its geometry
        :return: all factories information in dictionary format (json)
        """
        lyr = self.conn.GetLayer(DataLoader.lyr_factory)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_factory, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return None
        else:
            # print(lyr)
            rt_factories = dict()
            feature_count = lyr.GetFeatureCount()
            print("# of factories: ", feature_count)
            # lyr_defn = lyr.GetLayerDefn()
            # for i in range(lyr_defn.GetFieldCount()):
            #     print(lyr_defn.GetFieldDefn(i).GetName())
            for feature in lyr:
                feature_json = json.loads(feature.ExportToJson())
                # get the id and name, and save them in a dictionary
                obj_id = feature_json['id']
                rt_factories[obj_id] = Factory(feature_json)
            # important: reset the reading
            lyr.ResetReading()
            return rt_factories

    def get_factories_products(self, factories, reactions, chemicals, emission_info):
        """
        read gaolanport.factory_reaction_product to get all the products information
        :param factories:
        :param reactions: dictionary of reaction formula's
        :param chemicals: dictionary of all chemicals
        :param emission_info: dictionary of all emission data
        :return:
        """
        sql = 'select b.*, c.name_en, c.name_cn from ' + DataLoader.lyr_factory + ' a, ' \
              + DataLoader.lyr_factory_reaction_product + ' b, ' + DataLoader.lyr_chemical + ' c ' \
              + 'where a.object_id=b.factory_id AND b.desired_chemical_id=c.object_id'
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR SQL]: ", sql , self.__db_name, "@", self.__db_server)
            return
        else:
            if __debug__:
                lyr_defn = lyr.GetLayerDefn()
                for i in range(lyr_defn.GetFieldCount()):
                    print(lyr_defn.GetFieldDefn(i).GetName())
            for feature in lyr:
                factory_id = feature.GetField('factory_id')
                rf_id = feature.GetField('reaction_formula_id')
                # check
                if rf_id not in reactions:
                    print("[ERROR]: No reaction formula is found for ", rf_id)
                if factory_id in factories:
                    factories[factory_id].add_product_line(feature, rf_id, reactions, chemicals)
                else:
                    print('[ERROR]: Unknown factory id in table', DataLoader.lyr_factory_reaction_product)
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)
            # add the factory byproducts, emission of each product line
            for factory in factories.values():
                factory.calculate_byproducts_per_product_line(chemicals)
                factory.calculate_emission_per_product_line(emission_info)

    # todo:
    def get_factories_utilities(self, factories, utilities_info, chemicals_info):
        """
        read the gaolanport.factory_reaction_utility table
        :param factories: {id: Factory instance}
        :param utilities_info: {object_id: UtilityType instance}
        :param chemicals_info: {chemical_id: Chemical instance}
        :return:
        """
        sql = "select * from " + DataLoader.lyr_factory_reaction_utility
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_factory_reaction_utility, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return None
        else:
            # print(lyr)
            if __debug__:
                feature_count = lyr.GetFeatureCount()
                print("# of factory utility: ", feature_count)
            for feature in lyr:
                factory_id = feature.GetField('factory_id')
                rf_id = feature.GetField('reaction_formula_id')
                utility_obj_id = feature.GetField('utility_type_id')    # key for in utilities_info
                # check
                if utility_obj_id not in utilities_info:
                    print('[warning]: Unknown ', utility_obj_id, ' in utility_type table')
                    continue
                if factory_id not in factories:
                    print('[warning]: Unknown ', factory_id, ' in factory table')
                    continue
                else:
                    factories[factory_id].store_utilities(rf_id, utility_obj_id)
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)
            for factory in factories.values():
                factory.calculate_utilities_per_product_line(utilities_info, chemicals_info)

    # Deprecated
    def get_factory_products(self, factory_id):
        sql = 'select b.*, c.name_en, c.name_cn from ' + DataLoader.lyr_factory + ' a, ' \
              + DataLoader.lyr_factory_reaction_product + ' b, ' + DataLoader.lyr_chemical + ' c ' \
              + 'where a.object_id=b.factory_id AND a.object_id=' + str(factory_id) \
              + ' AND b.desired_chemical_id=c.object_id'
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR SQL]: ", sql , self.__db_name, "@", self.__db_server)
            return
        else:
            feature_count = lyr.GetFeatureCount()
            factory_products = []
            print("# of factories: ", feature_count)
            for feature in lyr:
                feature_json = json.loads(feature.ExportToJson())
                # print(feature_json)
                factory_products.append(feature_json)
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)
            return factory_products

    def get_utility_type(self):
        """
        read the gaolanport.utility_type table information and save into a dictionary
        :return: {object_id: UtilityType instance}
        """
        sql = "select * from " + DataLoader.lyr_utility_type
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_utility_type, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return None
        else:
            # print(lyr)
            if __debug__:
                feature_count = lyr.GetFeatureCount()
                print("# of utility types: ", feature_count)
            rt_util_types = {}
            for feature in lyr:
                obj_id = feature.GetField('object_id')
                rt_util_types[obj_id] = UtilityType(feature)
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)
            return rt_util_types

if __name__ == "__main__":
    get_all_drivers()
    db = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
    all_chemicals = db.get_all_chemicals()
    all_reactions = db.get_all_reaction_formulas()
    all_utility_info = db.get_utility_type()
    all_emission_data = db.get_emission_data()

    # get factories
    test_factories = db.get_factories()
    # get products of all factories
    db.get_factories_products(test_factories, all_reactions, all_chemicals, all_emission_data)
    db.get_factories_utilities(test_factories, all_utility_info, all_chemicals)
    db.get_factory_products(2)
    db.close()


