from datetime import datetime
import uuid
import json
from models import App, AppWithId
from tools import AppsCouchdbBackend

apps = AppsCouchdbBackend()

#--------------
def create_test_item():
    item = AppWithId(
        name="winzip",
        manufacturer="winzip",
        opensource=False,
        created=datetime.now(),
        category="Others"
    )
    apps.add_item(item=item)

#--------------
def upate_test_item():
    item = AppWithId(
        name="winzip",
        manufacturer="winzip",
        version="667",
        opensource=False,
        category="Others"
    )
    apps.update_item(id=uuid.UUID("37a3c6ee2780476993022cdab9d3ec08"), item=item)

#--------------
def print_data_items():
    for item in apps.data:
        print(item.model_dump())




if __name__ == "__main__":
    # pass
    # create_test_item()
    # upate_test_item()
    # print_data_items()
    apps.delete_item(id=uuid.UUID("68f22158c0de3cea6de6227c97000f68"))
       
