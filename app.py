from flask import Flask, request, render_template_string
import xml.etree.ElementTree as ET
from xml.dom import minidom

app = Flask(__name__)

XML_FILE = "transport.xml"

def get_stations():
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    stations = {}
    for s in root.findall("stations/station"):
        stations[s.get("id")] = s.get("name")
    return stations

def get_all_trips():
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    stations = get_stations()
    result = []
    for line in root.findall("lines/line"):
        dep = stations.get(line.get("departure"), "?")
        arr = stations.get(line.get("arrival"), "?")
        for trip in line.findall("trips/trip"):
            sched = trip.find("schedule")
            classes = []
            for c in trip.findall("class"):
                classes.append({
                    "type": c.get("type"),
                    "price": int(c.get("price"))
                })
            prices = [c["price"] for c in classes]
            result.append({
                "line": line.get("code"),
                "departure": dep,
                "arrival": arr,
                "code": trip.get("code"),
                "type": trip.get("type"),
                "dep_time": sched.get("departure") if sched is not None else "",
                "arr_time": sched.get("arrival") if sched is not None else "",
                "days": trip.findtext("days", ""),
                "classes": classes,
                "min_price": min(prices) if prices else 0,
            })
    return result

def get_trip_by_code(code):
    dom = minidom.parse(XML_FILE)
    stations = get_stations()
    for line_el in dom.getElementsByTagName("line"):
        for trip_el in line_el.getElementsByTagName("trip"):
            if trip_el.getAttribute("code") == code:
                sched_list = trip_el.getElementsByTagName("schedule")
                dep_time = ""
                arr_time = ""
                if sched_list:
                    dep_time = sched_list[0].getAttribute("departure")
                    arr_time = sched_list[0].getAttribute("arrival")
                days_el = trip_el.getElementsByTagName("days")
                days = ""
                if days_el:
                    days = days_el[0].firstChild.nodeValue
                classes = []
                for c in trip_el.getElementsByTagName("class"):
                    classes.append({
                        "type": c.getAttribute("type"),
                        "price": c.getAttribute("price")
                    })
                dep = stations.get(line_el.getAttribute("departure"), "?")
                arr = stations.get(line_el.getAttribute("arrival"), "?")
                return {
                    "code": code,
                    "line": line_el.getAttribute("code"),
                    "type": trip_el.getAttribute("type"),
                    "departure": dep,
                    "arrival": arr,
                    "dep_time": dep_time,
                    "arr_time": arr_time,
                    "days": days,
                    "classes": classes,
                }
    return None

def get_stats():
    trips = get_all_trips()
    lines = {}
    types = {}
    for t in trips:
        lcode = t["line"]
        if lcode not in lines:
            lines[lcode] = {
                "dep": t["departure"],
                "arr": t["arrival"],
                "cheapest": t,
                "priciest": t
            }
        else:
            if t["min_price"] < lines[lcode]["cheapest"]["min_price"]:
                lines[lcode]["cheapest"] = t
            if t["min_price"] > lines[lcode]["priciest"]["min_price"]:
                lines[lcode]["priciest"] = t
        ttype = t["type"]
        if ttype in types:
            types[ttype] += 1
        else:
            types[ttype] = 1
    return lines, types



HOME = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Railway Trips</title>
<style>
body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
nav { background: #2c3e50; padding: 10px 20px; margin-bottom: 20px; }
nav a { color: white; margin-right: 15px; text-decoration: none; }
nav a:hover { text-decoration: underline; }
h2 { margin-bottom: 15px; }
table { border-collapse: collapse; width: 100%; background: white; }
th { background: #2c3e50; color: white; padding: 8px 12px; }
td { padding: 8px 12px; border-bottom: 1px solid #ddd; }
tr:hover { background: #fff0f0; }
a.btn { background: #c0392b; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-size: 0.85em;}
</style>
</head>
<body>
<nav>
  <a href="/">All Trips</a>
  <a href="/search">Search</a>
  <a href="/filter">Filter</a>
  <a href="/stats">Stats</a>
</nav>
<h2>All Trips</h2>
<table>
  <tr><th>Code</th><th>Line</th><th>From</th><th>To</th><th>Type</th><th>Schedule</th><th>Min Price</th><th></th></tr>
  {% for t in trips %}
  <tr>
    <td>{{ t.code }}</td>
    <td>{{ t.line }}</td>
    <td>{{ t.departure }}</td>
    <td>{{ t.arrival }}</td>
    <td>{{ t.type }}</td>
    <td>{{ t.dep_time }} - {{ t.arr_time }}</td>
    <td>{{ t.min_price }} DA</td>
    <td><a class="btn" href="/trip/{{ t.code }}">Details</a></td>
  </tr>
  {% endfor %}
</table>
</body>
</html>
"""

SEARCH = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Search Trip</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;}
nav { background: #2c3e50; padding: 10px 20px; margin-bottom: 20px; }
nav a { color: white; margin-right: 15px; text-decoration: none; }
input { padding: 6px; margin-right: 10px; }
button { padding: 6px 16px; background: #c0392b; color: white; border: none; cursor: pointer; }
.box { background: white; padding: 20px; margin-top: 20px; max-width: 600px; }
table { border-collapse: collapse; width: 100%; margin-top: 10px; }
th { background: #2c3e50; color: white; padding: 7px 10px; }
td { padding: 7px 10px; border-bottom: 1px solid #ddd; }
.err { color: red; margin-top: 10px; }
</style>
</head>
<body>
<nav>
  <a href="/">All Trips</a>
  <a href="/search">Search</a>
  <a href="/filter">Filter</a>
  <a href="/stats">Stats</a>
</nav>
<h2>Search Trip by Code</h2>
<form method="get">
  <input name="code" value="{{ code }}" placeholder="ex: T102"/>
  <button type="submit">Search</button>
</form>
{% if searched and not trip %}
  <p class="err">No trip found with code {{ code }}</p>
{% endif %}
{% if trip %}
<div class="box">
  <b>Trip: {{ trip.code }}</b><br>
  Line: {{ trip.line }} | Type: {{ trip.type }}<br>
  From: {{ trip.departure }} -> To: {{ trip.arrival }}<br>
  Schedule: {{ trip.dep_time }} - {{ trip.arr_time }}<br>
  Days: {{ trip.days }}<br>
  <table style="margin-top:10px">
    <tr><th>Class</th><th>Price (DA)</th></tr>
    {% for c in trip.classes %}
    <tr>
      <td>{{ c.type }}</td>
      <td>{{ c.price }}</td>
    </tr>
    {% endfor %}
  </table>
</div>
{% endif %}
</body>
</html>
"""

FILTER = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Filter Trips</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;}
nav { background: #2c3e50; padding: 10px 20px; margin-bottom: 20px; }
nav a { color: white; margin-right: 15px; text-decoration: none; }
.form-row { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px; align-items: flex-end; }
.form-row label { display: block; font-size: 0.85em; margin-bottom: 3px; }
select, input[type=number] { padding: 6px; min-width: 150px; }
button { padding: 6px 16px; background: #c0392b; color: white; border: none; cursor: pointer; }
table { border-collapse: collapse; width: 100%; background: white; }
th { background: #2c3e50; color: white; padding: 8px 12px; }
td { padding: 8px 12px; border-bottom: 1px solid #ddd; }
</style>
</head>
<body>
<nav>
  <a href="/">All Trips</a>
  <a href="/search">Search</a>
  <a href="/filter">Filter</a>
  <a href="/stats">Stats</a>
</nav>
<h2>Filter Trips</h2>
<form method="get">
  <div class="form-row">
    <div>
      <label>From</label>
      <select name="dep">
        <option value="">-- any --</option>
        {% for s in stations %}
        <option value="{{ s }}" {% if dep==s %}selected{% endif %}>{{ s }}</option>
        {% endfor %}
      </select>
    </div>
    <div>
      <label>To</label>
      <select name="arr">
        <option value="">-- any --</option>
        {% for s in stations %}
        <option value="{{ s }}" {% if arr==s %}selected{% endif %}>{{ s }}</option>
        {% endfor %}
      </select>
    </div>
    <div>
      <label>Type</label>
      <select name="ttype">
        <option value="">-- any --</option>
        {% for t in types %}
        <option value="{{ t }}" {% if ttype==t %}selected{% endif %}>{{ t }}</option>
        {% endfor %}
      </select>
    </div>
    <div>
      <label>Max Price (DA)</label>
      <input type="number" name="max_price" value="{{ max_price }}" placeholder="ex: 1500"/>
    </div>
    <button type="submit">Filter</button>
    <a href="/filter">Reset</a>
  </div>
</form>
{% if trips %}
<table>
  <tr><th>Code</th><th>From</th><th>To</th><th>Type</th><th>Schedule</th><th>Days</th><th>Min Price</th></tr>
  {% for t in trips %}
  <tr>
    <td>{{ t.code }}</td>
    <td>{{ t.departure }}</td>
    <td>{{ t.arrival }}</td>
    <td>{{ t.type }}</td>
    <td>{{ t.dep_time }} - {{ t.arr_time }}</td>
    <td>{{ t.days }}</td>
    <td>{{ t.min_price }} DA</td>
  </tr>
  {% endfor %}
</table>
{% else %}
<p>No results.</p>
{% endif %}
</body>
</html>
"""

STATS = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Statistics</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;}
nav { background: #2c3e50; padding: 10px 20px; margin-bottom: 20px; }
nav a { color: white; margin-right: 15px; text-decoration: none; }
.box { background: white; padding: 15px 20px; margin-bottom: 15px; border-left: 4px solid #c0392b;}
table { border-collapse: collapse; }
th { background: #2c3e50; color: white; padding: 7px 12px; }
td { padding: 7px 12px; border-bottom: 1px solid #ddd; }
</style>
</head>
<body>
<nav>
  <a href="/">All Trips</a>
  <a href="/search">Search</a>
  <a href="/filter">Filter</a>
  <a href="/stats">Stats</a>
</nav>
<h2>Statistics</h2>
<h3>Number of trips per type</h3>
<table style="margin-bottom:25px; background:white;">
  <tr><th>Type</th><th>Count</th></tr>
  {% for ttype, cnt in types.items() %}
  <tr><td>{{ ttype }}</td><td>{{ cnt }}</td></tr>
  {% endfor %}
</table>
<h3>Cheapest and most expensive per line</h3>
{% for lcode, info in lines.items() %}
<div class="box">
  <b>Line {{ lcode }}: {{ info.dep }} -> {{ info.arr }}</b><br><br>
  Cheapest: {{ info.cheapest.code }} ({{ info.cheapest.type }}) - {{ info.cheapest.min_price }} DA<br>
  Most expensive: {{ info.priciest.code }} ({{ info.priciest.type }}) - {{ info.priciest.min_price }} DA
</div>
{% endfor %}
</body>
</html>
"""

TRIP_DETAIL = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Trip Detail</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;}
nav { background: #2c3e50; padding: 10px 20px; margin-bottom: 20px; }
nav a { color: white; margin-right: 15px; text-decoration: none; }
.box { background: white; padding: 20px; max-width: 550px; }
table { border-collapse: collapse; width: 100%; margin-top: 12px; }
th { background: #2c3e50; color: white; padding: 7px 10px; }
td { padding: 7px 10px; border-bottom: 1px solid #ddd; }
a { color: #c0392b; }
</style>
</head>
<body>
<nav>
  <a href="/">All Trips</a>
  <a href="/search">Search</a>
  <a href="/filter">Filter</a>
  <a href="/stats">Stats</a>
</nav>
<h2>Trip Details</h2>
{% if trip %}
<div class="box">
  <p><b>Code:</b> {{ trip.code }}</p>
  <p><b>Line:</b> {{ trip.line }}</p>
  <p><b>Type:</b> {{ trip.type }}</p>
  <p><b>From:</b> {{ trip.departure }}</p>
  <p><b>To:</b> {{ trip.arrival }}</p>
  <p><b>Schedule:</b> {{ trip.dep_time }} - {{ trip.arr_time }}</p>
  <p><b>Days:</b> {{ trip.days }}</p>
  <table>
    <tr><th>Class</th><th>Price (DA)</th></tr>
    {% for c in trip.classes %}
    <tr><td>{{ c.type }}</td><td>{{ c.price }}</td></tr>
    {% endfor %}
  </table>
</div>
{% else %}
<p>Trip not found.</p>
{% endif %}
<br><a href="/">Back</a>
</body>
</html>
"""


@app.route("/")
def home():
    trips = get_all_trips()
    return render_template_string(HOME, trips=trips)

@app.route("/search")
def search():
    code = request.args.get("code", "").strip().upper()
    searched = "code" in request.args
    trip = None
    if code:
        trip = get_trip_by_code(code)
    return render_template_string(SEARCH, code=code, trip=trip, searched=searched)

@app.route("/filter")
def filter_trips():
    all_trips = get_all_trips()

    stations = sorted(set([t["departure"] for t in all_trips] + [t["arrival"] for t in all_trips]))
    types = sorted(set(t["type"] for t in all_trips))

    dep = request.args.get("dep", "")
    arr = request.args.get("arr", "")
    ttype = request.args.get("ttype", "")
    max_price = request.args.get("max_price", "")

    trips = all_trips

    if dep:
        trips = [t for t in trips if t["departure"] == dep]
    if arr:
        trips = [t for t in trips if t["arrival"] == arr]
    if ttype:
        trips = [t for t in trips if t["type"] == ttype]
    if max_price:
        try:
            mp = int(max_price)
            trips = [t for t in trips if t["min_price"] <= mp]
        except:
            pass 

    return render_template_string(FILTER, trips=trips, stations=stations,
                                  types=types, dep=dep, arr=arr,
                                  ttype=ttype, max_price=max_price)

@app.route("/stats")
def stats():
    lines, types = get_stats()
    return render_template_string(STATS, lines=lines, types=types)

@app.route("/trip/<code>")
def trip_detail(code):
    trip = get_trip_by_code(code.upper())
    return render_template_string(TRIP_DETAIL, trip=trip)


if __name__ == "__main__":
    app.run(debug=True)
