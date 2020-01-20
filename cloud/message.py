def message(text):
    import http.client
    import json
    conn = http.client.HTTPSConnection("api.chatbot.com")
    payload = "{\"query\":\"%s\",\"sessionId\":\"1034021451\",\"storyId\":\"5deac04611addd0007848990\"}" % text
    headers = {
        'content-type': "application/json",
        'authorization': "Bearer yyk1z9EqauPFlf6HHBfj2ZmdwVl0ldiO"
        }
    conn.request("POST", "/query", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_dec = json.loads(data.decode())
    answer = data_dec['result']['interaction']['name']
    return answer
