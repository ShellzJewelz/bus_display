import httpx
from defines import BUS_GOV_LANGUAGE_HEBREW, BUS_GOV_LANGUAGE_ENGLISH

import random

def test_generate_dummy_rows():
    dummy_rows = [               
        {
            "operator": "Extra", 
            "route": "67", 
            "arrivals": "1, 8, 14"
        },
        {
            "operator": "Extra", 
            "route": "71", 
            "arrivals": "1, 8, 14"
        },
        {
            "operator": "Metropolin", 
            "route": "611", 
            "arrivals": "1, 8, 14"
        }
    ]

    rows = []
    r = random.randint(1, len(dummy_rows))
    for i in range(0, r):
        rows.append(dummy_rows[i])

    return rows

class GovILBusStopScraper(object):
	__URL_BASE = "https://bus.gov.il/WebApi/api/passengerinfo/" 
	__GET_STOP_INFO = __URL_BASE + "GetBusStopByMakat/{0}/{1}/false"
	__GET_REALTIME = __URL_BASE + "GetRealtimeBusLineListByBustop/{0}/{1}/false"

	def __init__(self, stopCode: int, busFilter: dict[int, list[str]], language):

		self.stopCode = stopCode
		self.url = self.__GET_REALTIME.format(stopCode, language)
		self.busFilter = busFilter
		self.__scrapedData = []

		with httpx.Client() as client:
			try:
				response = client.get(self.__GET_STOP_INFO.format(stopCode, language), timeout=30)
				result = response.json()
				self.stopName = result["Name"]
			except:
				self.stopName = "Unknown Bus Stop Name"

	def filterResults(self, results):
		for result in results:
			if result["CompanyId"] in self.busFilter.keys():
				if result["Shilut"] in self.busFilter[result["CompanyId"]]:
					yield result

	def __buildInfoTable(self, results):
		for result in results:
			yield {
				"operator": result["CompanyName"], 
				"route": result["Shilut"], 
				"arrivals": ", ".join([str(m) for m in result["MinutesToArrivalList"]])
			}

	def scrape(self):
		with httpx.Client() as client:
			response = client.get(self.url, timeout=30)

		try:
			results = response.json()
			results = self.filterResults(results)
			self.__scrapedData = list(self.__buildInfoTable(results))

		except Exception as e:
			raise e
	
	def getScrapedData(self):
		return self.__scrapedData

def main():
	pass

if __name__ == "__main__":
	main()