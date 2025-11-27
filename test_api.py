from utils.api_handler import get_live_matches

def main():
    data = get_live_matches()
    if not data:
        print("No data returned or API error.")
        return

    print("✅ Live API call success.")
    # Print just a small part so terminal won't explode
    print(str(data)[:1000])

if __name__ == "__main__":
    main()
