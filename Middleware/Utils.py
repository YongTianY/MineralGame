import uuid
import json

def getCmdTemplate(params,method):    
    return json.dumps({"jsonrpc":"2.0","params":params,"id":str(uuid.uuid1()),"method":method})

