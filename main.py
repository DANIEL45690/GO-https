import os
import sys
import time
import json
import socket
import hashlib
import base64
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print(
        "\033[93m[!] requests library not installed. Run: pip install requests\033[0m"
    )
    sys.exit(1)


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"

    class FG:
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        BRIGHT_BLACK = "\033[90m"
        BRIGHT_RED = "\033[91m"
        BRIGHT_GREEN = "\033[92m"
        BRIGHT_YELLOW = "\033[93m"
        BRIGHT_BLUE = "\033[94m"
        BRIGHT_MAGENTA = "\033[95m"
        BRIGHT_CYAN = "\033[96m"
        BRIGHT_WHITE = "\033[97m"

    class BG:
        BLACK = "\033[40m"
        RED = "\033[41m"
        GREEN = "\033[42m"
        YELLOW = "\033[43m"
        BLUE = "\033[44m"
        MAGENTA = "\033[45m"
        CYAN = "\033[46m"
        WHITE = "\033[47m"
        BRIGHT_BLACK = "\033[100m"
        BRIGHT_RED = "\033[101m"
        BRIGHT_GREEN = "\033[102m"
        BRIGHT_YELLOW = "\033[103m"
        BRIGHT_BLUE = "\033[104m"
        BRIGHT_MAGENTA = "\033[105m"
        BRIGHT_CYAN = "\033[106m"
        BRIGHT_WHITE = "\033[107m"


class Gradient:
    @staticmethod
    def linear(
        text: str, start_rgb: Tuple[int, int, int], end_rgb: Tuple[int, int, int]
    ) -> str:
        result = []
        length = len(text)
        for i, char in enumerate(text):
            ratio = i / length if length > 1 else 0
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            result.append(f"\033[38;2;{r};{g};{b}m{char}")
        result.append(Colors.RESET)
        return "".join(result)

    @staticmethod
    def rainbow(text: str) -> str:
        result = []
        for i, char in enumerate(text):
            hue = (i * 5) % 360
            r, g, b = Gradient._hsv_to_rgb(hue, 1.0, 1.0)
            result.append(f"\033[38;2;{r};{g};{b}m{char}")
        result.append(Colors.RESET)
        return "".join(result)

    @staticmethod
    def fire(text: str) -> str:
        colors = [
            (255, 0, 0),
            (255, 69, 0),
            (255, 140, 0),
            (255, 165, 0),
            (255, 215, 0),
        ]
        return Gradient._horizontal(text, colors)

    @staticmethod
    def ice(text: str) -> str:
        colors = [
            (0, 255, 255),
            (0, 191, 255),
            (30, 144, 255),
            (70, 130, 180),
            (100, 149, 237),
        ]
        return Gradient._horizontal(text, colors)

    @staticmethod
    def neon(text: str) -> str:
        colors = [
            (57, 255, 20),
            (0, 255, 127),
            (0, 255, 255),
            (127, 255, 0),
            (50, 205, 50),
        ]
        return Gradient._horizontal(text, colors)

    @staticmethod
    def sunset(text: str) -> str:
        colors = [
            (255, 94, 77),
            (255, 121, 63),
            (255, 160, 0),
            (255, 190, 11),
            (238, 210, 2),
        ]
        return Gradient._horizontal(text, colors)

    @staticmethod
    def _horizontal(text: str, colors: List[Tuple[int, int, int]]) -> str:
        result = []
        length = len(text)
        segments = len(colors)
        for i, char in enumerate(text):
            idx = int((i / length) * (segments - 1)) if length > 0 else 0
            r, g, b = colors[idx]
            result.append(f"\033[38;2;{r};{g};{b}m{char}")
        result.append(Colors.RESET)
        return "".join(result)

    @staticmethod
    def _hsv_to_rgb(h: int, s: float, v: float) -> Tuple[int, int, int]:
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


class Animation:
    @staticmethod
    def spinner(duration: float = 1.0, message: str = "Processing"):
        frames = ["◐", "◓", "◑", "◒"]
        start = time.time()
        i = 0
        while time.time() - start < duration:
            sys.stdout.write(
                f"\r{Gradient.neon(frames[i % len(frames)])} {Gradient.linear(message, (0,255,255), (255,0,255))}"
            )
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")

    @staticmethod
    def progress_bar(total: int = 100, duration: float = 1.5, title: str = "Progress"):
        bar_length = 50
        for i in range(total + 1):
            percent = i / total
            filled = int(bar_length * percent)
            bar = "█" * filled + "░" * (bar_length - filled)
            if percent < 0.33:
                grad_bar = Gradient.linear(bar, (255, 0, 0), (255, 165, 0))
            elif percent < 0.66:
                grad_bar = Gradient.linear(bar, (255, 165, 0), (255, 255, 0))
            else:
                grad_bar = Gradient.linear(bar, (255, 255, 0), (0, 255, 0))
            sys.stdout.write(
                f"\r{Gradient.linear(title, (0,255,255), (255,255,0))} : {grad_bar} {i:3d}%"
            )
            sys.stdout.flush()
            time.sleep(duration / total)
        print()

    @staticmethod
    def typewriter(text: str, delay: float = 0.02):
        for char in text:
            sys.stdout.write(Gradient.rainbow(char))
            sys.stdout.flush()
            time.sleep(delay)
        print()


class Banner:
    @staticmethod
    def show():
        banner = """
   ▄██████▄   ▄██████▄        ▄███████▄     ▄████████    ▄███████▄    ▄████████  ▄██████▄     ▄████████
  ███    ███ ███    ███      ██▀     ▄██   ███    ███   ███    ███   ███    ███ ███    ███   ███    ███
  ███    █▀  ███    ███            ▄███▀   ███    ███   ███    ███   ███    ███ ███    ███   ███    █▀
 ▄███        ███    ███       ▀█▀▄███▀▄▄   ███    ███   ███    ███  ▄███▄▄▄▄██▀ ███    ███   ███
▀▀███ ████▄  ███    ███        ▄███▀   ▀ ▀███████████ ▀█████████▀  ▀▀███▀▀▀▀▀   ███    ███ ▀███████████
  ███    ███ ███    ███      ▄███▀         ███    ███   ███        ▀███████████ ███    ███          ███
  ███    ███ ███    ███      ███▄     ▄█   ███    ███   ███          ███    ███ ███    ███    ▄█    ███
  ████████▀   ▀██████▀        ▀████████▀   ███    █▀   ▄████▀        ███    ███  ▀██████▀   ▄████████▀
                                                                     ███    ███
        """
        lines = banner.split("\n")
        for line in lines:
            if line.strip():
                grad = Gradient.linear(line, (0, 255, 255), (255, 0, 255))
                print(grad)
            time.sleep(0.01)

    @staticmethod
    def small():
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                    GO-STYLE HTTP TOOLKIT v2.0                    ║
╠══════════════════════════════════════════════════════════════════╣
║  Author: @console_hack          Functions: 50+                   ║
║  Status: Active                  Library: requests               ║
╚══════════════════════════════════════════════════════════════════╝
        """
        for line in banner.split("\n"):
            if line.strip():
                print(Gradient.neon(line))
            time.sleep(0.005)


class GoStyleHTTP:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
            }
        )
        self.timeout = 30

    def get(self, url: str, params: Dict = None) -> Dict:
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            return {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text[:500] + "..." if len(resp.text) > 500 else resp.text,
                "json": (
                    resp.json()
                    if "application/json" in resp.headers.get("Content-Type", "")
                    else None
                ),
                "time": resp.elapsed.total_seconds(),
                "url": resp.url,
            }
        except Exception as e:
            return {"error": str(e)}

    def post(self, url: str, data: Dict = None, json_data: Dict = None) -> Dict:
        try:
            resp = self.session.post(
                url, data=data, json=json_data, timeout=self.timeout
            )
            return {
                "status": resp.status_code,
                "body": resp.text[:500],
                "json": resp.json() if resp.text else None,
                "time": resp.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"error": str(e)}

    def put(self, url: str, json_data: Dict = None) -> Dict:
        try:
            resp = self.session.put(url, json=json_data, timeout=self.timeout)
            return {
                "status": resp.status_code,
                "body": resp.text[:300],
                "time": resp.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"error": str(e)}

    def delete(self, url: str) -> Dict:
        try:
            resp = self.session.delete(url, timeout=self.timeout)
            return {"status": resp.status_code, "body": resp.text[:300]}
        except Exception as e:
            return {"error": str(e)}

    def patch(self, url: str, json_data: Dict = None) -> Dict:
        try:
            resp = self.session.patch(url, json=json_data, timeout=self.timeout)
            return {"status": resp.status_code, "body": resp.text[:300]}
        except Exception as e:
            return {"error": str(e)}

    def head(self, url: str) -> Dict:
        try:
            resp = self.session.head(url, timeout=self.timeout)
            return {"status": resp.status_code, "headers": dict(resp.headers)}
        except Exception as e:
            return {"error": str(e)}

    def options(self, url: str) -> Dict:
        try:
            resp = self.session.options(url, timeout=self.timeout)
            return {"status": resp.status_code, "allow": resp.headers.get("Allow", "")}
        except Exception as e:
            return {"error": str(e)}

    def download(self, url: str, filename: str) -> bool:
        try:
            resp = self.session.get(url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = (downloaded / total) * 100
                            bar = "█" * int(percent // 2) + "░" * (
                                50 - int(percent // 2)
                            )
                            sys.stdout.write(
                                f'\r{Gradient.linear(f"Download: {bar}", (0,255,0), (255,215,0))} {percent:.1f}%'
                            )
                            sys.stdout.flush()
            print()
            return True
        except Exception as e:
            print(f"\nError: {e}")
            return False

    def upload(self, url: str, filepath: str) -> Dict:
        try:
            with open(filepath, "rb") as f:
                files = {"file": (os.path.basename(filepath), f)}
                resp = self.session.post(url, files=files)
                return {"status": resp.status_code, "body": resp.text[:300]}
        except Exception as e:
            return {"error": str(e)}

    def batch_get(self, urls: List[str]) -> List[Dict]:
        results = []
        for url in urls:
            results.append(self.get(url))
        return results

    def parallel_get(self, urls: List[str], workers: int = 5) -> List[Dict]:
        from concurrent.futures import ThreadPoolExecutor

        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.get, url) for url in urls]
            for future in futures:
                results.append(future.result())
        return results

    def check_status(self, url: str) -> int:
        try:
            resp = self.session.head(url, timeout=5)
            return resp.status_code
        except:
            return 0

    def get_size(self, url: str) -> int:
        try:
            resp = self.session.head(url, timeout=5)
            return int(resp.headers.get("content-length", 0))
        except:
            return 0

    def get_content_type(self, url: str) -> str:
        try:
            resp = self.session.head(url, timeout=5)
            return resp.headers.get("content-type", "unknown")
        except:
            return "unknown"

    def get_server(self, url: str) -> str:
        try:
            resp = self.session.head(url, timeout=5)
            return resp.headers.get("server", "unknown")
        except:
            return "unknown"

    def get_last_modified(self, url: str) -> str:
        try:
            resp = self.session.head(url, timeout=5)
            return resp.headers.get("last-modified", "unknown")
        except:
            return "unknown"

    def get_ip(self, url: str) -> str:
        try:
            host = url.replace("http://", "").replace("https://", "").split("/")[0]
            return socket.gethostbyname(host)
        except:
            return "unknown"

    def get_redirects(self, url: str, max_follow: int = 10) -> List[str]:
        redirects = []
        current = url
        for _ in range(max_follow):
            try:
                resp = self.session.get(current, allow_redirects=False)
                if resp.status_code in [301, 302, 303, 307, 308]:
                    next_url = resp.headers.get("Location", "")
                    if next_url:
                        redirects.append(next_url)
                        current = next_url
                    else:
                        break
                else:
                    break
            except:
                break
        return redirects

    def set_cookie(self, name: str, value: str):
        self.session.cookies.set(name, value)

    def clear_cookies(self):
        self.session.cookies.clear()

    def set_header(self, key: str, value: str):
        self.session.headers[key] = value

    def remove_header(self, key: str):
        if key in self.session.headers:
            del self.session.headers[key]

    def get_headers(self) -> Dict:
        return dict(self.session.headers)

    def set_timeout(self, seconds: int):
        self.timeout = seconds

    def set_proxy(self, proxy_url: str):
        self.session.proxies = {"http": proxy_url, "https": proxy_url}

    def remove_proxy(self):
        self.session.proxies = {}

    def set_auth(self, username: str, password: str):
        self.session.auth = (username, password)

    def remove_auth(self):
        self.session.auth = None

    def extract_links(self, html: str) -> List[str]:
        pattern = r'href=[\'"]?([^\'" >]+)'
        return re.findall(pattern, html)

    def extract_images(self, html: str) -> List[str]:
        pattern = r'src=[\'"]?([^\'" >]+)'
        return re.findall(pattern, html)

    def extract_emails(self, text: str) -> List[str]:
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(pattern, text)

    def get_md5(self, url: str) -> str:
        result = self.get(url)
        if "body" in result:
            return hashlib.md5(result["body"].encode()).hexdigest()
        return ""

    def get_sha256(self, url: str) -> str:
        result = self.get(url)
        if "body" in result:
            return hashlib.sha256(result["body"].encode()).hexdigest()
        return ""

    def base64_encode(self, text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    def base64_decode(self, encoded: str) -> str:
        return base64.b64decode(encoded).decode()

    def url_encode(self, text: str) -> str:
        return requests.utils.quote(text)

    def url_decode(self, text: str) -> str:
        return requests.utils.unquote(text)

    def spider(self, start_url: str, max_pages: int = 20) -> List[str]:
        visited = set()
        to_visit = [start_url]
        found = []

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            result = self.get(url)
            if "body" in result:
                links = self.extract_links(result["body"])
                for link in links:
                    if (
                        link.startswith("http")
                        and link not in visited
                        and link not in to_visit
                    ):
                        to_visit.append(link)
                found.append(url)
        return found

    def benchmark(self, url: str, count: int = 20) -> Dict:
        times = []
        successes = 0
        for i in range(count):
            Animation.spinner(0.05, f"Test {i+1}/{count}")
            start = time.time()
            result = self.get(url)
            elapsed = time.time() - start
            if "error" not in result:
                successes += 1
                times.append(elapsed)
        return {
            "min": min(times) if times else 0,
            "max": max(times) if times else 0,
            "avg": sum(times) / len(times) if times else 0,
            "success_rate": (successes / count) * 100,
            "total": count,
            "successful": successes,
        }

    def compare(self, url1: str, url2: str) -> Dict:
        r1 = self.get(url1)
        r2 = self.get(url2)
        return {
            "status_match": r1.get("status") == r2.get("status"),
            "size_match": len(r1.get("body", "")) == len(r2.get("body", "")),
            "time_diff": abs(r1.get("time", 0) - r2.get("time", 0)),
        }

    def monitor(self, url: str, interval: int = 5, duration: int = 30) -> List[Dict]:
        results = []
        start_time = time.time()
        total_checks = duration // interval
        for i in range(total_checks):
            if time.time() - start_time > duration:
                break
            Animation.spinner(0.3, f"Monitor {i+1}/{total_checks}")
            result = self.get(url)
            result["timestamp"] = datetime.now().isoformat()
            results.append(result)
            time.sleep(interval)
        return results


class Menu:
    def __init__(self):
        self.http = GoStyleHTTP()
        self.running = True

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def header(self):
        self.clear()
        Banner.show()
        print()
        print(Gradient.fire("=" * 70))
        print(
            Gradient.rainbow(
                "          GO-STYLE HTTP TOOLKIT - ENTERPRISE EDITION          "
            )
        )
        print(Gradient.ice("=" * 70))
        print(
            f"{Colors.FG.BRIGHT_CYAN}│{Colors.RESET} {Colors.BOLD}Author:{Colors.RESET} @console_hack          {Colors.FG.BRIGHT_GREEN}Status:{Colors.RESET} Active"
        )
        print(
            f"{Colors.FG.BRIGHT_CYAN}│{Colors.RESET} {Colors.BOLD}Version:{Colors.RESET} 2.0                  {Colors.FG.BRIGHT_YELLOW}Features:{Colors.RESET} 50+ Functions"
        )
        print(Gradient.fire("=" * 70))

    def menu(self):
        items = [
            ("1", "GET Request"),
            ("2", "POST Request"),
            ("3", "PUT Request"),
            ("4", "DELETE Request"),
            ("5", "PATCH Request"),
            ("6", "HEAD Request"),
            ("7", "OPTIONS Request"),
            ("8", "Download File"),
            ("9", "Upload File"),
            ("10", "Batch GET"),
            ("11", "Parallel GET"),
            ("12", "Check Status"),
            ("13", "Get Size"),
            ("14", "Content Type"),
            ("15", "Server Info"),
            ("16", "Last Modified"),
            ("17", "IP Lookup"),
            ("18", "Follow Redirects"),
            ("19", "Set Cookie"),
            ("20", "Clear Cookies"),
            ("21", "View Headers"),
            ("22", "Set Header"),
            ("23", "Remove Header"),
            ("24", "Set Timeout"),
            ("25", "Set Proxy"),
            ("26", "Remove Proxy"),
            ("27", "Set Auth"),
            ("28", "Remove Auth"),
            ("29", "Extract Links"),
            ("30", "Extract Images"),
            ("31", "Extract Emails"),
            ("32", "Get MD5"),
            ("33", "Get SHA256"),
            ("34", "Base64 Encode"),
            ("35", "Base64 Decode"),
            ("36", "URL Encode"),
            ("37", "URL Decode"),
            ("38", "Web Spider"),
            ("39", "Benchmark"),
            ("40", "Compare URLs"),
            ("41", "Monitor URL"),
            ("42", "System Info"),
            ("43", "Clear Screen"),
            ("0", "Exit"),
        ]

        left = items[: len(items) // 2]
        right = items[len(items) // 2 :]

        print(Gradient.neon("\n┌" + "─" * 68 + "┐"))
        for i in range(max(len(left), len(right))):
            left_text = ""
            right_text = ""
            if i < len(left):
                left_text = f"{left[i][0]:<3} {left[i][1]}"
            if i < len(right):
                right_text = f"{right[i][0]:<3} {right[i][1]}"

            left_padded = left_text.ljust(32)
            right_padded = right_text.ljust(32)

            left_colored = Gradient.linear(left_padded, (0, 255, 255), (100, 255, 100))
            right_colored = Gradient.ice(right_padded)
            print(f"│ {left_colored} {right_colored} │")
        print(Gradient.neon("└" + "─" * 68 + "┘"))

        return input(
            f"\n{Colors.FG.BRIGHT_GREEN}┌─[{Colors.FG.BRIGHT_YELLOW}@console_hack{Colors.FG.BRIGHT_GREEN}]\n└─$ {Colors.RESET}"
        )

    def result(self, data: Dict):
        print(Gradient.sunset("\n┌" + "─" * 68 + "┐"))
        print(f"│ {Colors.BOLD}RESULT:{Colors.RESET}".ljust(69) + "│")
        print(Gradient.fire("├" + "─" * 68 + "┤"))
        i = 0
        for key, value in data.items():
            if value is not None and i < 15:
                val_str = str(value)
                if len(val_str) > 55:
                    val_str = val_str[:52] + "..."
                print(f"│ {Colors.FG.BRIGHT_CYAN}{key}:{Colors.RESET} {val_str:<60} │")
                i += 1
        print(Gradient.sunset("└" + "─" * 68 + "┘"))
        input(
            f"\n{Colors.FG.BRIGHT_MAGENTA}[!] Press Enter to continue...{Colors.RESET}"
        )

    def run_get(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        Animation.spinner(0.5, "Fetching")
        res = self.http.get(url)
        self.result(res)

    def run_post(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        choice = input(
            f"{Colors.FG.BRIGHT_CYAN}[?] JSON or FORM? (j/f): {Colors.RESET}"
        ).lower()
        if choice == "j":
            json_str = input(f"{Colors.FG.BRIGHT_CYAN}[?] JSON data: {Colors.RESET}")
            json_data = json.loads(json_str) if json_str else {}
            res = self.http.post(url, json_data=json_data)
        else:
            data_str = input(
                f"{Colors.FG.BRIGHT_CYAN}[?] Form data (key=value, comma): {Colors.RESET}"
            )
            data = {}
            if data_str:
                for pair in data_str.split(","):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        data[k.strip()] = v.strip()
            res = self.http.post(url, data=data)
        self.result(res)

    def run_put(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        json_str = input(f"{Colors.FG.BRIGHT_CYAN}[?] JSON data: {Colors.RESET}")
        json_data = json.loads(json_str) if json_str else None
        res = self.http.put(url, json_data)
        self.result(res)

    def run_delete(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        res = self.http.delete(url)
        self.result(res)

    def run_patch(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        json_str = input(f"{Colors.FG.BRIGHT_CYAN}[?] JSON data: {Colors.RESET}")
        json_data = json.loads(json_str) if json_str else None
        res = self.http.patch(url, json_data)
        self.result(res)

    def run_head(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        res = self.http.head(url)
        self.result(res)

    def run_options(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        res = self.http.options(url)
        self.result(res)

    def run_download(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] File URL: {Colors.RESET}")
        filename = input(f"{Colors.FG.BRIGHT_CYAN}[?] Save as: {Colors.RESET}")
        success = self.http.download(url, filename)
        if success:
            print(f"{Colors.FG.BRIGHT_GREEN}✓ Downloaded: {filename}{Colors.RESET}")
        else:
            print(f"{Colors.FG.BRIGHT_RED}✗ Download failed{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_upload(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] Upload URL: {Colors.RESET}")
        filepath = input(f"{Colors.FG.BRIGHT_CYAN}[?] File path: {Colors.RESET}")
        if os.path.exists(filepath):
            Animation.progress_bar(100, 1.0, "Uploading")
            res = self.http.upload(url, filepath)
            self.result(res)
        else:
            print(f"{Colors.FG.BRIGHT_RED}File not found!{Colors.RESET}")
            input(f"\nPress Enter...")

    def run_batch(self):
        urls = []
        print(f"{Colors.FG.BRIGHT_CYAN}Enter URLs (empty to stop):{Colors.RESET}")
        while True:
            url = input("> ")
            if not url:
                break
            urls.append(url)
        Animation.progress_bar(100, 1.5, "Batch Processing")
        results = self.http.batch_get(urls)
        for i, res in enumerate(results):
            status = res.get("status", "error")
            color = Colors.FG.BRIGHT_GREEN if status == 200 else Colors.FG.BRIGHT_RED
            print(f"{color}{urls[i]}: {status}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_parallel(self):
        urls = []
        print(f"{Colors.FG.BRIGHT_CYAN}Enter URLs (empty to stop):{Colors.RESET}")
        while True:
            url = input("> ")
            if not url:
                break
            urls.append(url)
        workers = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Workers (1-10): {Colors.RESET}") or "5"
        )
        workers = min(10, max(1, workers))
        Animation.spinner(1.0, "Parallel requests")
        results = self.http.parallel_get(urls, workers)
        for i, res in enumerate(results):
            status = res.get("status", "error")
            color = Colors.FG.BRIGHT_GREEN if status == 200 else Colors.FG.BRIGHT_RED
            print(
                f"{color}{urls[i]}: {status} ({res.get('time', 0):.2f}s){Colors.RESET}"
            )
        input(f"\nPress Enter...")

    def run_status(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        status = self.http.check_status(url)
        color = (
            Colors.FG.BRIGHT_GREEN
            if status == 200
            else Colors.FG.BRIGHT_RED if status > 0 else Colors.FG.BRIGHT_YELLOW
        )
        print(f"{color}Status: {status}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_size(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        size = self.http.get_size(url)
        if size > 1024 * 1024:
            size_str = f"{size/(1024*1024):.2f} MB"
        elif size > 1024:
            size_str = f"{size/1024:.2f} KB"
        else:
            size_str = f"{size} B"
        print(f"{Colors.FG.BRIGHT_GREEN}Size: {size_str}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_content_type(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        ctype = self.http.get_content_type(url)
        print(f"{Colors.FG.BRIGHT_GREEN}Content-Type: {ctype}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_server(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        server = self.http.get_server(url)
        print(f"{Colors.FG.BRIGHT_GREEN}Server: {server}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_last_modified(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        modified = self.http.get_last_modified(url)
        print(f"{Colors.FG.BRIGHT_GREEN}Last-Modified: {modified}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_ip(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        ip = self.http.get_ip(url)
        print(f"{Colors.FG.BRIGHT_GREEN}IP Address: {ip}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_redirects(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        max_follow = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Max follows: {Colors.RESET}") or "10"
        )
        redirects = self.http.get_redirects(url, max_follow)
        if redirects:
            print(Gradient.rainbow("\nRedirect Chain:"))
            for i, r in enumerate(redirects):
                print(f"{Colors.FG.BRIGHT_YELLOW}{i+1}.{Colors.RESET} {r}")
        else:
            print(f"{Colors.FG.BRIGHT_GREEN}No redirects{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_set_cookie(self):
        name = input(f"{Colors.FG.BRIGHT_CYAN}[?] Cookie name: {Colors.RESET}")
        value = input(f"{Colors.FG.BRIGHT_CYAN}[?] Cookie value: {Colors.RESET}")
        self.http.set_cookie(name, value)
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Cookie set{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_clear_cookies(self):
        self.http.clear_cookies()
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Cookies cleared{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_view_headers(self):
        headers = self.http.get_headers()
        print(Gradient.neon("\nCurrent Headers:"))
        for k, v in headers.items():
            print(f"{Colors.FG.BRIGHT_CYAN}{k}:{Colors.RESET} {v}")
        input(f"\nPress Enter...")

    def run_set_header(self):
        key = input(f"{Colors.FG.BRIGHT_CYAN}[?] Header name: {Colors.RESET}")
        value = input(f"{Colors.FG.BRIGHT_CYAN}[?] Header value: {Colors.RESET}")
        self.http.set_header(key, value)
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Header set{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_remove_header(self):
        key = input(f"{Colors.FG.BRIGHT_CYAN}[?] Header name: {Colors.RESET}")
        self.http.remove_header(key)
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Header removed{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_set_timeout(self):
        timeout = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Timeout seconds: {Colors.RESET}")
        )
        self.http.set_timeout(timeout)
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Timeout set to {timeout}s{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_set_proxy(self):
        proxy = input(
            f"{Colors.FG.BRIGHT_CYAN}[?] Proxy URL (http://ip:port): {Colors.RESET}"
        )
        self.http.set_proxy(proxy)
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Proxy set{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_remove_proxy(self):
        self.http.remove_proxy()
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Proxy removed{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_set_auth(self):
        user = input(f"{Colors.FG.BRIGHT_CYAN}[?] Username: {Colors.RESET}")
        password = input(f"{Colors.FG.BRIGHT_CYAN}[?] Password: {Colors.RESET}")
        self.http.set_auth(user, password)
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Auth set{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_remove_auth(self):
        self.http.remove_auth()
        print(f"{Colors.FG.BRIGHT_GREEN}✓ Auth removed{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_extract_links(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        res = self.http.get(url)
        if "body" in res:
            links = self.http.extract_links(res["body"])
            print(Gradient.rainbow(f"\nFound {len(links)} links:"))
            for link in links[:30]:
                print(f"{Colors.FG.BRIGHT_CYAN}→{Colors.RESET} {link}")
        input(f"\nPress Enter...")

    def run_extract_images(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        res = self.http.get(url)
        if "body" in res:
            images = self.http.extract_images(res["body"])
            print(Gradient.rainbow(f"\nFound {len(images)} images:"))
            for img in images[:30]:
                print(f"{Colors.FG.BRIGHT_MAGENTA}🖼️{Colors.RESET} {img}")
        input(f"\nPress Enter...")

    def run_extract_emails(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        res = self.http.get(url)
        if "body" in res:
            emails = self.http.extract_emails(res["body"])
            print(Gradient.rainbow(f"\nFound {len(emails)} emails:"))
            for email in emails:
                print(f"{Colors.FG.BRIGHT_GREEN}✉️{Colors.RESET} {email}")
        input(f"\nPress Enter...")

    def run_md5(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        Animation.spinner(0.5, "Calculating MD5")
        md5 = self.http.get_md5(url)
        print(f"{Colors.FG.BRIGHT_GREEN}MD5: {md5}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_sha256(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        Animation.spinner(0.5, "Calculating SHA256")
        sha256 = self.http.get_sha256(url)
        print(f"{Colors.FG.BRIGHT_GREEN}SHA256: {sha256}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_b64encode(self):
        text = input(f"{Colors.FG.BRIGHT_CYAN}[?] Text to encode: {Colors.RESET}")
        encoded = self.http.base64_encode(text)
        print(f"{Colors.FG.BRIGHT_GREEN}Encoded: {encoded}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_b64decode(self):
        text = input(f"{Colors.FG.BRIGHT_CYAN}[?] Base64 to decode: {Colors.RESET}")
        try:
            decoded = self.http.base64_decode(text)
            print(f"{Colors.FG.BRIGHT_GREEN}Decoded: {decoded}{Colors.RESET}")
        except:
            print(f"{Colors.FG.BRIGHT_RED}Invalid Base64{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_urlencode(self):
        text = input(f"{Colors.FG.BRIGHT_CYAN}[?] Text to encode: {Colors.RESET}")
        encoded = self.http.url_encode(text)
        print(f"{Colors.FG.BRIGHT_GREEN}Encoded: {encoded}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_urldecode(self):
        text = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL to decode: {Colors.RESET}")
        decoded = self.http.url_decode(text)
        print(f"{Colors.FG.BRIGHT_GREEN}Decoded: {decoded}{Colors.RESET}")
        input(f"\nPress Enter...")

    def run_spider(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] Start URL: {Colors.RESET}")
        max_pages = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Max pages: {Colors.RESET}") or "20"
        )
        Animation.progress_bar(100, 2.0, "Spider crawling")
        found = self.http.spider(url, max_pages)
        print(Gradient.rainbow(f"\nDiscovered {len(found)} pages:"))
        for page in found:
            print(f"{Colors.FG.BRIGHT_CYAN}📄{Colors.RESET} {page}")
        input(f"\nPress Enter...")

    def run_benchmark(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL: {Colors.RESET}")
        count = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Requests count: {Colors.RESET}") or "20"
        )
        count = min(100, max(1, count))
        print(Gradient.neon("\nRunning benchmark..."))
        result = self.http.benchmark(url, count)
        self.result(result)

    def run_compare(self):
        url1 = input(f"{Colors.FG.BRIGHT_CYAN}[?] First URL: {Colors.RESET}")
        url2 = input(f"{Colors.FG.BRIGHT_CYAN}[?] Second URL: {Colors.RESET}")
        Animation.spinner(1.0, "Comparing")
        result = self.http.compare(url1, url2)
        self.result(result)

    def run_monitor(self):
        url = input(f"{Colors.FG.BRIGHT_CYAN}[?] URL to monitor: {Colors.RESET}")
        interval = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Interval (sec): {Colors.RESET}") or "5"
        )
        duration = int(
            input(f"{Colors.FG.BRIGHT_CYAN}[?] Duration (sec): {Colors.RESET}") or "30"
        )
        results = self.http.monitor(url, interval, duration)
        print(Gradient.rainbow(f"\nMonitor Results ({len(results)} samples):"))
        for res in results:
            status = res.get("status", "error")
            color = Colors.FG.BRIGHT_GREEN if status == 200 else Colors.FG.BRIGHT_RED
            print(
                f"{res.get('timestamp')} - {color}Status: {status} ({res.get('time', 0):.2f}s){Colors.RESET}"
            )
        input(f"\nPress Enter...")

    def run_info(self):
        print(Gradient.ice("\n" + "═" * 60))
        print(f"{Colors.BOLD}System Information:{Colors.RESET}")
        print(
            f"  Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        print(f"  OS: {os.name}")
        print(f"  Requests Version: {requests.__version__}")
        print(f"  Session Headers: {len(self.http.get_headers())}")
        print(f"  Timeout: {self.http.timeout}s")
        print(f"  Proxy: {'Enabled' if self.http.session.proxies else 'Disabled'}")
        print(f"  Auth: {'Enabled' if self.http.session.auth else 'Disabled'}")
        print(Gradient.ice("═" * 60))
        input(f"\nPress Enter...")

    def run_clear(self):
        self.clear()
        Banner.small()
        time.sleep(0.5)

    def exit_app(self):
        self.running = False
        print(Gradient.fire("\n\n" + "█" * 70))
        print(Gradient.neon("          Thank you for using Go-Style HTTP Toolkit!"))
        print(Gradient.sunset("          Created by @console_hack"))
        print(Gradient.fire("█" * 70 + "\n"))
        sys.exit(0)

    def main(self):
        handlers = {
            "1": self.run_get,
            "2": self.run_post,
            "3": self.run_put,
            "4": self.run_delete,
            "5": self.run_patch,
            "6": self.run_head,
            "7": self.run_options,
            "8": self.run_download,
            "9": self.run_upload,
            "10": self.run_batch,
            "11": self.run_parallel,
            "12": self.run_status,
            "13": self.run_size,
            "14": self.run_content_type,
            "15": self.run_server,
            "16": self.run_last_modified,
            "17": self.run_ip,
            "18": self.run_redirects,
            "19": self.run_set_cookie,
            "20": self.run_clear_cookies,
            "21": self.run_view_headers,
            "22": self.run_set_header,
            "23": self.run_remove_header,
            "24": self.run_set_timeout,
            "25": self.run_set_proxy,
            "26": self.run_remove_proxy,
            "27": self.run_set_auth,
            "28": self.run_remove_auth,
            "29": self.run_extract_links,
            "30": self.run_extract_images,
            "31": self.run_extract_emails,
            "32": self.run_md5,
            "33": self.run_sha256,
            "34": self.run_b64encode,
            "35": self.run_b64decode,
            "36": self.run_urlencode,
            "37": self.run_urldecode,
            "38": self.run_spider,
            "39": self.run_benchmark,
            "40": self.run_compare,
            "41": self.run_monitor,
            "42": self.run_info,
            "43": self.run_clear,
            "0": self.exit_app,
        }

        while self.running:
            self.header()
            choice = self.menu()
            if choice in handlers:
                self.clear()
                Banner.small()
                handlers[choice]()
            elif choice:
                print(f"{Colors.FG.BRIGHT_RED}Invalid choice!{Colors.RESET}")
                time.sleep(1)


if __name__ == "__main__":
    app = Menu()
    try:
        app.main()
    except KeyboardInterrupt:
        print(Gradient.fire("\n\nInterrupted by user"))
        sys.exit(0)
