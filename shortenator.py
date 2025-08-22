import os
import random
import string
import time
import urllib.request
import urllib.error
import subprocess
from typing import Optional

HTML_TEMPLATE = """<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>deze link is verkort met mijn geweldige website</title>
    <link rel=\"stylesheet\" href=\"css.css\">
</head>
<body>
    <noscript><a href=\"{url}\">geen js? geen probleem!</a></noscript>
    <script>window.location.href = \"{url}\";</script>
</body>
</html>"""


def generate_name() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))


def pick_name(initial: Optional[str]) -> str:
    naam = initial or ""
    while os.path.exists(f"{naam}.html") or not naam:
        if not naam:
            naam = generate_name()
        else:
            naam = input("deze naam is al in gebruik, voer een andere naam in (voer niks in voor random)\n") or ""
    return naam


def write_file(filename: str, target_url: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(url=target_url))


def run_git_commands(filename: str) -> None:
    # Stage
    try:
        subprocess.run(["git", "add", filename], check=True)
    except subprocess.CalledProcessError as e:
        print(f"kon bestand niet toevoegen aan git: {e}")
        return

    # Commit if there is something staged
    diff_index = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    if filename not in diff_index.stdout.split():
        print("bestand is niet gestaged, commit wordt overgeslagen")
        return
    subprocess.run(["git", "commit", "-m", f"Add shortened link {filename}"], check=False)
    # Push (ignore failure so script continues with polling)
    subprocess.run(["git", "push"], check=False)


def poll_url(url: str, delay: int = 5, timeout: int = 180) -> bool:
    start = time.time()
    while True:
        try:
            with urllib.request.urlopen(url) as resp:  # nosec B310 (simple GET)
                if resp.status == 200:
                    return True
        except urllib.error.HTTPError as e:
            if e.code not in (403, 404):
                print(f"HTTP fout: {e.code}")
        except urllib.error.URLError:
            pass
        elapsed = time.time() - start
        if elapsed > timeout:
            print("timeout bereikt voordat de link beschikbaar was")
            return False
        print("je link is nog niet beschikbaar, probeer het over 5 seconden opnieuw (Ctrl+C om te stoppen)")
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            print("onderbroken door gebruiker")
            return False


def main():
    link = input("wat is de link die je wilt verkorten\n")
    naam_input = input("naam van de verkorting (voer niks in voor random)\n")
    naam = pick_name(naam_input)
    filename = f"{naam}.html"
    write_file(filename, link)
    print(f"je link is verkort naar {filename}")
    run_git_commands(filename)
    print("je link is geupload naar github (als push geslaagd is)")

    # kleine buffer voor GitHub Pages deploy
    time.sleep(10)
    try:
        with open("CNAME", "r", encoding="utf-8") as f:
            cname = f.read().strip()
    except FileNotFoundError:
        print("CNAME bestand niet gevonden; kan publieke URL niet bepalen")
        return
    url = f"https://{cname}/{filename}"
    if poll_url(url):
        print(f"je link is nu beschikbaar op {url}")
    else:
        print(f"kon de link niet bevestigen, probeer later: {url}")


if __name__ == "__main__":
    main()