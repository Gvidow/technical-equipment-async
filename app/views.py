from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests

import os
from dotenv import load_dotenv

from concurrent import futures

CALLBACK_URL = "http://0.0.0.0:8080/api/v1/stocks/edit/"
ACCESS_TOKEN_KEY = "TE_INTERNAL_ACCESS_TOKEN"
load_dotenv()

executor = futures.ThreadPoolExecutor(max_workers=1)

def get_random_status(req_id):
    time.sleep(5)
    return {
      "id": req_id,
      "status": random.uniform(0, 1) < 0.8,
    }

def status_callback(task):
    try:
      result = task.result()
      print(result)
    except futures._base.CancelledError:
      return
    
    nurl = str(CALLBACK_URL+str(result["id"]))
    access_token = os.environ.get(ACCESS_TOKEN_KEY, "")
    answer = {"is_reverted": result["status"], "access_token": access_token}
    requests.put(nurl, json=answer, timeout=3)

@api_view(['POST'])
def set_status(request):
    if "request_id" in request.data.keys():   
        id = request.data["request_id"]        
        task = executor.submit(get_random_status, id)
        task.add_done_callback(status_callback)        
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
