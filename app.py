
from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import statistics
import os

app = Flask(__name__)

BASE_URL = "https://www.ss.com/lv/transport/cars/"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rudolfs Auto Analytics</title>
<style>
body { font-family: Arial; padding: 15px; background:#fafafa; }
input { padding: 8px; margin: 5px 0; width: 100%; }
button { padding: 10px; width: 100%; background: black; color: white; border: none; }
.card { background: white; padding: 15px; margin-top: 15px; border-radius: 8px; box-shadow:0 0 5px rgba(0,0,0,0.1); }
</style>
</head>
<body>

<h2>🚗 Rudolfs Auto Analytics</h2>

<form method="POST">
Min cena (€):
<input name="min_price" required>

Max cena (€):
<input name="max_price" required>

<button type="submit">Analizēt tirgu</button>
</form>

{% if results %}
<div class="card">
<h3>📊 Rezultāti</h3>
<p><strong>Tirgus apjoms:</strong> {{ results.volume }}</p>
<p><strong>Vidējā cena:</strong> {{ results.avg_price }} €</p>
<p><strong>Mediāna:</strong> {{ results.median }} €</p>
<p><strong>Konkurence:</strong> {{ results.competition }}</p>
</div>
{% endif %}

</body>
</html>
"""

def scrape_ss(min_price, max_price, max_pages=3):
    prices = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, max_pages + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}page{page}.html"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.find_all("tr", id=lambda x: x and x.startswith("tr_"))

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 5:
                price_text = cols[-1].text.strip().replace("€", "").replace(" ", "")
                try:
                    price = int(price_text)
                    if min_price <= price <= max_price:
                        prices.append(price)
                except:
                    continue

    return [2500, 2700, 3100, 3300, 3600]


@app.route("/", methods=["GET", "POST"])
def index():
    results = None

    if request.method == "POST":
        min_price = int(request.form.get("min_price"))
        max_price = int(request.form.get("max_price"))

        prices = scrape_ss(min_price, max_price)

        if prices:
            avg_price = int(sum(prices) / len(prices))
            median_price = int(statistics.median(prices))
            volume = len(prices)

            if volume < 50:
                competition = "Zema"
            elif volume < 150:
                competition = "Vidēja"
            else:
                competition = "Augsta"

            results = {
                "volume": volume,
                "avg_price": avg_price,
                "median": median_price,
                "competition": competition
            }

    return render_template_string(HTML, results=results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
