import argparse
import subprocess
import requests

def print_banner():
    banner = r"""
  ____        _         
 |  _ \      | |        
 | |_) |_   _| |_ _   _ 
 |  _ <| | | | __| | | |
 | |_) | |_| | |_| |_| |
 |____/ \__,_|\__|\__,_|

   D-Bust - Directory & Subdomain Bruter
   """
    print(banner)

def check_http_status(subdomain):
    try:
        response = requests.get(f"http://{subdomain}", timeout=2)
        return response.status_code
    except requests.RequestException:
        return "N/A"

def run_external_tool(domain):
    try:
        result = subprocess.run(
            ["gobuster", "dns", "-d", domain, "-w", "/usr/share/wordlists/dirb/common.txt", "-q"],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.splitlines():
            if line.strip():  # Ensure line is not empty
                subdomain = line.split()[-1]
                status = check_http_status(subdomain)
                print(f"Found: {subdomain} | Status: {status}")
    except FileNotFoundError:
        print("[!] Required tool not found. Please install it and try again.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running external tool: {e}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Subdomain Enumerator")
    parser.add_argument("-d", "--domain", required=True, help="Target domain")
    args = parser.parse_args()
    
    print(f"[*] Enumerating subdomains for {args.domain}...")
    run_external_tool(args.domain)

if __name__ == "__main__":
    main()

