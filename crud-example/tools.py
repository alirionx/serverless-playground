import os
import json
from uuid import UUID

from settings import settings
from models import App, AppWithId


#---------------------------------------------
class AppsFileBackend:
    def __init__(self) -> None:
        self.data_file_path = os.path.join(settings.data_dir_path, "apps.json")
        self.data = []
        self.check_data_source()
        self.load_data()

    #-------------------------
    def check_data_source(self) -> None:
        os.makedirs(settings.data_dir_path, exist_ok=True)
        if not os.path.isfile(self.data_file_path):
            with open(self.data_file_path, "w") as fl:
                fl.write("[]")
            return
        try:
            with open(self.data_file_path, "r") as fl:
                json.loads(fl.read())
        except:
            with open(self.data_file_path, "w") as fl:
                fl.write("[]")
        
    #-------------------------
    def load_data(self) -> None:
        with open(self.data_file_path, "r") as fl:
            str_data = fl.read()
        data = json.loads(str_data)
        self.data = [ AppWithId(**item) for item in data]
    
    #-------------------------
    def save_data(self) -> None:
        with open(self.data_file_path, "w") as fl:
            data = [ item.model_dump() for item in self.data ]
            str_data = json.dumps(data, indent=2, default=str)
            fl.write(str_data)
        
    #-------------------------
    def add_item(self, item:AppWithId) -> None:
        if item.id in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' alredy exists" %item.id)
        self.data.append(item)
        self.save_data()

    #-------------------------
    def get_item(self, id:UUID) -> AppWithId:
        if id not in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' does not exist" %id)
        for entry in self.data:
            if id == entry.id:
                return entry

    #-------------------------
    def update_item(self, id:UUID, item:AppWithId) -> AppWithId:
        if id not in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' does not exist" %id)
        item.id = id
        for entry in self.data:
            if id == entry.id:
                self.data[self.data.index(entry)] = item
        self.save_data()
        return item

    #-------------------------
    def delete_item(self, id:UUID) -> None:
        if id not in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' does not exist" %id)
        for entry in self.data:
            if id == entry.id:
                del self.data[self.data.index(entry)] 
        self.save_data()

    #-------------------------



#---------------------------------------------
class AppsCouchdbBackend:
    from couchdb import Server
    def __init__(self) -> None:
        self.db_cli = None
        self.data = []
        self.create_db_cli()
        self.load_data()

    #-------------------------
    def create_db_cli(self):
        couchdb_server = self.Server(settings.couchdb_connection_string)
        if settings.couchdb_database_name in couchdb_server:
            self.db_cli = couchdb_server[settings.couchdb_database_name]
        else:
            self.db_cli = couchdb_server.create(settings.couchdb_database_name)
        self.db_cli.resource.session.disable_ssl_verification()

    #-------------------------
    def load_data(self) -> None:
        self.data = []
        for _id in self.db_cli:
            entry = self.db_cli[_id]
            entry["id"] = UUID(_id)
            item = AppWithId(**entry)
            self.data.append(item)

    #-------------------------
    def add_item(self, item:AppWithId) -> None:
        if item.id in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' alredy exists" %item.id)
        self.data.append(item)
        entry = json.loads(item.model_dump_json())
        entry["_id"] = item.id.hex
        del entry["id"]
        self.db_cli.save(entry)
    
    #-------------------------
    def get_item(self, id:UUID) -> AppWithId:
        if id not in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' does not exist" %id)
        for entry in self.data:
            if id == entry.id:
                return entry
    
    #-------------------------
    def update_item(self, id:UUID, item:AppWithId) -> AppWithId:
        if id not in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' does not exist" %id)
        item.id = id
        for entry in self.data:
            if id == entry.id:
                self.data[self.data.index(entry)] = item
        #------
        entry = json.loads(item.model_dump_json())
        entry["_id"] = item.id.hex
        del entry["id"]
        doc = self.db_cli[item.id.hex]
        doc.update(**entry)
        self.db_cli[item.id.hex] = doc
        return item
    
    #-------------------------
    def delete_item(self, id:UUID) -> None:
        if id not in [entry.id for entry in self.data ]:
            raise Exception("Item with id '%s' does not exist" %id)
        for entry in self.data:
            if id == entry.id:
                del self.data[self.data.index(entry)] 
        self.db_cli.delete(self.db_cli[id.hex])
    
    #-------------------------

#---------------------------------------------