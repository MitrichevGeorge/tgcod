import re
import requests
from bs4 import BeautifulSoup
import json
import os
import tempfile

FILE_PATH = "proxies.json"


def save_proxies_to_file(proxies, path=FILE_PATH):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(e)
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def load_proxies_from_file(path=FILE_PATH):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def getproxy():
    url = "https://spys.one/en/socks-proxy-list/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    xx0_input = soup.find("input", {"name": "xx0"})
    if not xx0_input or "value" not in xx0_input.attrs:
        return []

    xx0_value = xx0_input["value"]

    data = {
        "xx0": xx0_value,
        "xpp": "3",
        "xf1": "0",
        "xf2": "0",
        "xf4": "0",
        "xf5": "2"
    }

    try:
        res = requests.post(url, headers=headers, data=data, timeout=10)
        res.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.find_all("tr", class_=re.compile(r"spy1x|spy1xx"))
    if not rows:
        return []

    js_vars = {}
    js_code = soup.find("script", string=re.compile(r"\w+\s*=\s*\d+\^\w+;"))
    if js_code:
        for var, a, b in re.findall(r"(\w+)\s*=\s*(\d+)\^(\w+);", js_code.string):
            js_vars[var] = int(a) ^ js_vars.get(b, 0)
    else:
        return []

    proxies = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        ip_tag = cols[0].find("font", class_="spy14")
        if not ip_tag:
            continue

        ip = ip_tag.text.strip()
        port_script = ip_tag.find_next("script")
        port = ""
        if port_script and port_script.string:
            for a, b in re.findall(r"\((\w+)\^(\w+)\)", port_script.string):
                port += str(js_vars.get(a, 0) ^ js_vars.get(b, 0))

        proxy_type = cols[1].text.strip()
        country_tag = cols[3].find("font", class_="spy14") if len(cols) > 3 else None
        country = country_tag.text.strip() if country_tag else ""

        proxies.append({
            "ip": ip,
            "port": port,
            "type": proxy_type,
            "country": country
        })

    return proxies


def getproxy_cached():
    cached = load_proxies_from_file()
    if len(cached) < 1:
        print("nofile")
        proxies = getproxy()
        if proxies:
            save_proxies_to_file(proxies)
            return proxies

        cached = load_proxies_from_file()
    return cached


if __name__ == "__main__":
    proxies = getproxy_cached()
    for p in proxies:
        print(f"{p['ip']}:{p['port']} {p['type']} {p['country']}")
