import sys
import json
try:
    from osgeo import osr, ogr, gdal
except:
    sys.exit('Error: cannot find GDAL/OGR modules')

# enable GDAL/OGR exceptions
gdal.UseExceptions()


def get_all_drivers():
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

    def __init__(self, db_server, db_name, db_user, db_pwd):
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

    def get_factories(self):
        lyr = self.conn.GetLayer(DataLoader.lyr_factory)
        if lyr is None:
            print("[ERROR]: layer name", DataLoader.lyr_factory, "could not be found in database ", self.__db_name, "@", self.__db_server)
            return
        else:
            # print(lyr)
            feature_count = lyr.GetFeatureCount()
            feature_collection = {"type": "FeatureCollection", "features": []}
            print("# of factories: ", feature_count)
            for feature in lyr:
                feature_json = json.loads(feature.ExportToJson())
                # print(feature_json)
                feature_collection["features"].append(feature_json)
            # important: reset the reading
            lyr.ResetReading()
            return feature_collection


# if __name__ == "__main__":
#     get_all_drivers()
#     db_loader = DataLoader('localhost', 'CE_platform', 'Han', 'Han')
#     db_loader.get_factories()
#     db_loader.get_factories()
#     db_loader.close()


