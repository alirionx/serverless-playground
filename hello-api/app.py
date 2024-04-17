import json
import socket
from datetime import datetime
from dataclasses import dataclass
from flask import request, Flask

#------------------------------------------------------
@dataclass
class ApiStatus:
    message: str = None
    hostname: str = None
    request_host: str = None
    method: str = None
    statuscode: int = None
    timestamp: str = None
    args: str = None
    
#-------------------------------
def main(context=None):
    res = ApiStatus(
        message="Hello from the API",
        hostname=socket.gethostname(),
        request_host=request.host,
        method=request.method,
        statuscode=200,
        timestamp=str(datetime.now()),
        args=json.dumps(request.args)
    )

    return (json.dumps(res.__dict__), 200, 
        {"Content-Type": "application/json"} )

#--------------------------------
if __name__ == "__main__":
    app = Flask(__name__)
    @app.route('/')
    def hello_api():
        return main()
    app.run(host="0.0.0.0", port=8080)

#------------------------------------------------------
