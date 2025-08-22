import os
import random
import string
import time
import urllib.request
import urllib.error

link = input("wat is de link die je wilt verkorten\n")
naam = input("naam van de verkorting (voer niks in voor random)\n")
while os.path.exists(f"{naam}.html") or naam == "":
    if naam == "":
        naam = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    else:
        naam = input("deze naam is al in gebruik, voer een andere naam in (voer niks in voor random)\n")

base = f'''
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>deze link is verkort met mijn geweldige website</title>
</head>

<body>
    <noscript>
        <a href="{link}">geen js? geen probleem!</a>
    </noscript>
    <script>
        window.location.href = "{link}";
    </script>
    <link rel="stylesheet" href="css.css">
</body>

</html>
'''
with open(f"{naam}.html", "w") as f:
    f.write(base)
print(f"je link is verkort naar {naam}.html")
os.system("git commit -am 'verkort link'")
os.system("git push")

print("je link is geupload naar github")

with open("CNAME", "r") as f:
    cname = f.read().strip()

url = f"https://{cname}/{naam}.html"
while True:
    try:
        with urllib.request.urlopen(url) as resp:
            if resp.status == 200:
                break
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"HTTP fout: {e.code}")
    except urllib.error.URLError:
        pass
    print("je link is nog niet beschikbaar, probeer het over 5 seconden opnieuw")
    time.sleep(5)