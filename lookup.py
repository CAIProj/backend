import requests
import json
# parameter points: list of tupels (latitude, longitude)
# return value: list of altitudes
def lookup(points: list) -> list:
    if len(points) == 0:
        return []
    else:
        requ = "https://api.open-elevation.com/api/v1/lookup?locations="
        requ = requ + str(points[0][0]) + "," + str(points[0][1])
        for j in range(1, len(points)):
            requ = requ + "|" + str(points[j][0]) + "," + str(points[j][1])
        ok = False
        try:
            response = requests.get(requ)
            if response.ok:
                ok = True
        except requests.ConnectionError:
            pass
        if ok:
            response = json.loads(response.content)
            results = []
            for i in range(0, len(response["results"])):
               results.append(response["results"][i]["elevation"])
            return results
        else:
            print("open-elevation data could not be retrieved")
            return []
