import psycopg2


class DataSaver:
    """
        save data to database
    """
    table_chemical = "public.chemical"
    table_reaction_formula = "public.reaction_formula"
    table_reaction_product = "public.reaction_product"
    table_reaction_reactant = "public.reaction_reactant"
    table_reaction_emission = "public.emission_data"
    table_reaction_utility = "public.reaction_utility"

    def __init__(self, db_server, db_name, db_user, db_pwd):
        self.__db_server = db_server
        self.__db_name = db_name
        self.__db_user = db_user
        self.__db_pwd = db_pwd
        try:
            self.conn = psycopg2.connect(dbname=self.__db_name,
                                         host=self.__db_server,
                                         port=5432,
                                         user=db_user,
                                         password=db_pwd)
        except:
            print("Unable to connect to ", db_server)

    def close(self):
        self.conn.close()

    def reconnect(self):
        try:
            self.conn.close()
            self.conn = psycopg2.connect(dbname=self.__db_name,
                                         host=self.__db_server,
                                         port=5432,
                                         user=self.__db_user,
                                         password=self.__db_pwd)
            print("connection is reset.")
        except psycopg2.DatabaseError:
            print("Unable to reconnect to ", self.__db_server)

    def __is_record_existed(self, table_name, where_clause):
        sql = "select count(*) from " + table_name + " WHERE " + where_clause
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            count = cur.fetchone()[0]
            cur.close()
            if count > 0:
                return True
            else:
                return False
        except psycopg2.Error as e:
            print(e)
            return True

    def __get_max_id_of_table(self, id_field_name, table_name):
        """
        get the maximum value of %id_field_name% in table_name
        :param id_field_name: name of ID field
        :param table_name: 
        :return: maximum value of %id_field_name%
        """
        sql = "select max(" + id_field_name + ") from " + table_name
        cur = self.conn.cursor()
        cur.execute(sql)
        max_id = cur.fetchone()[0]
        cur.close()
        return max_id

    def update_chemical(self, content):
        """
        update existing chemical or insert new chemical into the public.chemical table
        :param content: 
        :return: True or False indicating succeed or failure
        """
        table_name = DataSaver.table_chemical # "public.test_chemical"  # DataSaver.lyr_chemical
        field_names = ["chem_id", "name_en", "name_cn", "molar_mass", "density", "symbol", "unit", "unit_cost",
                       "unit_transport_cost", "currency", "sp_heat"]
        chem_id = content["chem_id"]
        name_en = content["name_en"]
        name_cn = content["name_cn"]
        molar_mass = content["molar_mass"]
        density = content["density"]
        symbol = content["symbol"]
        unit = content["unit"]
        unit_cost = content["unit_cost"]
        unit_transport_cost = content["unit_transport_cost"]
        currency = content["currency"]
        sp_heat = content["sp_heat"]

        if chem_id is None:
            if self.__is_record_existed(table_name, "name_en='" + name_en + "' AND molar_mass=" + str(molar_mass)):
                print(name_en + " already existed in the table")
                return False, name_en + " already existed in the table"
            # e.g. insert into chemical values(15, 'Nitrogen',  '液氮', 28,   0, 'LN2', 'T', 200, NULL, 'EUR', NULL);
            new_obj_id = 1 + self.__get_max_id_of_table("object_id", table_name)
            sql = "INSERT INTO " + table_name + " VALUES(" \
                  + str(new_obj_id) + "," \
                  + "'" + name_en + "'," \
                  + "'" + name_cn + "'," \
                  + str(molar_mass) + "," \
                  + str(density) + "," \
                  + "'" + symbol + "'," \
                  + "'" + unit + "'," \
                  + str(unit_cost) + "," \
                  + str(unit_transport_cost) + "," \
                  + "'" + currency + "'," \
                  + str(sp_heat) + ")"
        else:
            sql = "UPDATE " + table_name + " SET " \
                  + "unit='" + unit + "'," \
                  + "unit_cost=" + str(unit_cost) + "," \
                  + "unit_transport_cost=" + str(unit_transport_cost) + "," \
                  + "cost_currency='" + currency + "'," \
                  + "sp_heat=" + str(sp_heat) \
                  + " WHERE object_id = " + chem_id
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            return True, ""
        except psycopg2.Error as e:
            print("Update chemical table failed[error code ", e.pgcode, "]")
            self.reconnect()
            return False, "Update chemical table failed[error code " + str(e.pgcode) + "]"

    def update_reaction_formula(self, content):
        """
        update/insert reaction formula
        :param content: 
        :return: 
        """
        rf_conditions = content['conditions']
        rf_catalysts = content['catalysts']
        rf_emissions = content['emissions']
        rf_reactants = content['reactants']
        rf_products = content['products']
        rf_utility = content['utilities']
        rf_upstream_process_ids = content['upstream_process']

        new_obj_id = 1 + self.__get_max_id_of_table("object_id", DataSaver.table_reaction_formula)
        new_emis_obj_id = 1 + self.__get_max_id_of_table("object_id", DataSaver.table_reaction_emission)
        # todo: update tables public.reaction_formula, public.reaction_product, public.reaction_reactant
        cur = self.conn.cursor()
        sql = "INSERT INTO " + DataSaver.table_reaction_formula \
              + "(object_id, description, temperature, pressure,heat_reaction, upstream_formula_ids)" \
              + " VALUES(" \
              + str(new_obj_id) + "," \
              + "'" + content['description'] + "'," \
              + str(rf_conditions['temperature']) + "," \
              + str(rf_conditions["pressure"]) + ","
        if rf_conditions["heat_reaction"] is None or rf_conditions["heat_reaction"] == '':
            sql += "null,"
        else:
            sql += "'" + str(rf_conditions["heat_reaction"]) + "',"
        if content['upstream_process'] is None or content['upstream_process'] == '':
            sql += "NULL);"
        else:
            sql += "'" + content['upstream_process'] + "');"

        for chem_id, quantity in rf_products.items():
            sql += "INSERT INTO " + DataSaver.table_reaction_product \
            + "(chemical_id,reaction_formula_id,quantity,unit,byproduct)" \
            + " VALUES(" + chem_id + "," + str(new_obj_id) + ",'" + str(quantity) + "'," + "'moles', false" + ");"
        for chem_id, quantity in rf_reactants.items():
            sql += "INSERT INTO " + DataSaver.table_reaction_reactant \
            + "(chemical_id,reaction_formula_id,quantity,unit,catalyst)" \
            + " VALUES(" + chem_id + "," + str(new_obj_id) + ",'" + str(quantity) + "'," + "'moles', false" + ");"
        for chem_id, quantity in rf_catalysts.items():
            sql += "INSERT INTO " + DataSaver.table_reaction_reactant \
            + "(chemical_id,reaction_formula_id,quantity,unit,byproduct)" \
            + " VALUES(" + chem_id + "," + str(new_obj_id) + ",'" + str(quantity) + "'," + "'moles', true" + ");"
        for emission in rf_emissions:
            sql += "INSERT INTO " + DataSaver.table_reaction_emission \
                   + "(object_id, reaction_formula_id,name_en,name_cn,unit,process,heat,electricity,total) VALUES(" \
                   + str(new_emis_obj_id) + "," + str(new_obj_id) + ",'" + emission["name"] + "','" + emission["name_cn"] \
                   + "','kg'," + str(emission["process"]) + "," + str(emission["heat"]) + "," + str(emission["electricity"]) + "," \
                   + str(emission["total"]) + ");"
            new_emis_obj_id += 1
        # for utilities in rf_utility:
        #     sql += "INSERT INTO " + DataSaver.table_reaction_reactant + "(object_id, name_en, name_cn,unit,unit_cost,cost_currency)" + " VALUES("
        try:
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            return True, ""
        except psycopg2.Error as e:
            return False, "Failed: Error code=" + str(e.pgcode)


# if __name__ == "__main__":
#     db = DataSaver('localhost', 'CE_platform', 'Han', 'Han')
#
#     test_content = {"chem_id": None, "name_en": 'Ethylene', "name_cn": '乙烯', "molar_mass":28,
#                     "density":1.26, "symbol":'C2H4', "unit":'T', "unit_cost":593, "unit_transport_cost":0,
#                     "currency":'EUR', "sp_heat":1530}
#     test_content1 = {"chem_id": None, "name_en": 'Nitrogen', "name_cn": '液氮', "molar_mass":28,
#                     "density":1.26, "symbol":'LN2', "unit":'T', "unit_cost":200, "unit_transport_cost":"NULL",
#                     "currency":'EUR', "sp_heat":"NULL"}
#     db.update_chemical(test_content)
#     db.update_chemical(test_content1)
#     db.update_chemical(test_content)
#     db.close()
