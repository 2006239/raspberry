from gpsdclient import GPSDClient

client = GPSDClient(host="127.0.0.1")
for result in client.dict_stream(convert_datetime=True, filter=["TPV"]):
	print("<time> %s" % result.get("time", "")+ "</time>")
	print("{ lat: %s" % result.get("lat", "")+ ", long: %s }" % result.get("lon", ""))

