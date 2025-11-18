# scripts/test_zillow.py

from dotenv import load_dotenv
load_dotenv()

from etl.zillow.fetch import fetch_zillow_listings


def main():
    props = fetch_zillow_listings()
    print(f"Got {len(props)} listings")
    if props:
        first = props[0]
        print("Sample keys:", list(first.keys()))
        print("First listing preview:")
        for k, v in list(first.items())[:15]:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()