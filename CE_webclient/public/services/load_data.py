import sys
import json
from services.factory_data import Factory
from services.chemical_data import Chemical
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
    lyr_chemical = 'public.chemical'
    lyr_reaction_formula = 'public.reaction_formula'
    lyr_reaction_reactant = 'public.reaction_reactant'

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
        self.conn = None

    def get_all_chemicals(self):
        """
        read the public.chemical table to get all the chemical information and save into a dictionary
        :return:
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

    def get_all_reaction_formulas(self):
        """
        read public.reaction_formula & public.reaction_reactant
        :return:
        """
        sql = 'select a.*, b.* from ' + DataLoader.lyr_reaction_formula + ' a,' \
              + DataLoader.lyr_reaction_reactant + ' b ' \
              + 'where a.object_id = b.reaction_formula_id'
        lyr = self.conn.ExecuteSQL(sql)
        if lyr is None:
            print("[ERROR SQL]: ", sql, self.__db_name, "@", self.__db_server)
            return None
        else:
            if __debug__:
                lyr_defn = lyr.GetLayerDefn()
                for i in range(lyr_defn.GetFieldCount()):
                    print(lyr_defn.GetFieldDefn(i).GetName())

            rt_reaction_formulas = {}
            for feature in lyr:
                formula_id = feature.GetField('object_id')
                if formula_id not in rt_reaction_formulas:
                    rt_reaction_formulas[formula_id] = ReactionFormula(feature)
                else:
                    rt_reaction_formulas[formula_id].add_reactant(feature)

            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)
            return rt_reaction_formulas

    def get_factories(self, rt_factories):
        """
        read gaolanport.factory table to get factory information including its geometry
        :param factories:
        :return: all factories information in dictionary format (json)
        """
        lyr = self.conn.GetLayer(DataLoader.lyr_factory)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_factory, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return None
        else:
            # print(lyr)
            feature_count = lyr.GetFeatureCount()
            print("# of factories: ", feature_count)

            # lyr_defn = lyr.GetLayerDefn()
            # for i in range(lyr_defn.GetFieldCount()):
            #     print(lyr_defn.GetFieldDefn(i).GetName())

            feature_collection = {"type": "FeatureCollection", "features": []}
            for feature in lyr:
                feature_json = json.loads(feature.ExportToJson())
                feature_collection["features"].append(feature_json)

                # get the id and name, and save them in a dictionary
                id = feature_json['id']
                rt_factories[id] = Factory(feature_json)

            # important: reset the reading
            lyr.ResetReading()
            return feature_collection

    def get_factories_products(self, factories, reactions, chemicals):
        """
        read gaolanport.factory_reaction_product to get all the products information
        :param factories:
        :param reactions: dictionary of reaction formula's
        :param chemicals: dictionary of all chemicals
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
                if factory_id in factories:
                    factories[factory_id].add_product(feature, reactions, chemicals)
            # important: reset the reading
            lyr.ResetReading()
            self.conn.ReleaseResultSet(lyr)

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


if __name__ == "__main__":
    get_all_drivers()
    db_loader = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
    all_chemicals = db_loader.get_all_chemicals()
    all_reactions = db_loader.get_all_reaction_formulas()

    test_factories = {}
    db_loader.get_factories(test_factories)

    db_loader.get_factories_products(test_factories, all_reactions, all_chemicals)
    db_loader.get_factory_products(2)
    db_loader.close()


