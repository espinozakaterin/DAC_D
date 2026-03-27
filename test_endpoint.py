import urllib.request
import urllib.error
import urllib.parse
from html.parser import HTMLParser

url = "http://127.0.0.1:8000/CWS/modulos/control/suministros/perfil/subir-foto"
data = b'test'

try:
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    print("Success:", response.read().decode())
except urllib.error.HTTPError as e:
    with open("error_output.html", "w", encoding="utf-8") as f:
        f.write(e.read().decode("utf-8", errors="ignore"))
    print(f"HTTP Error {e.code}: Wrote HTML to error_output.html")
except Exception as e:
    print(f"Other Error: {e}")
