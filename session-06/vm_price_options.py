#!/usr/bin/env python3
"""Every way to pay for one Linux VM size in one region, from the public Azure Retail Prices API.

    python3 vm_price_options.py Standard_D2s_v5 francecentral

No authentication and no dependencies beyond the standard library. Prices are USD list prices.
"""
import json
import sys
import urllib.parse
import urllib.request

HOURS_PER_MONTH = 730
API = "https://prices.azure.com/api/retail/prices"


def fetch(sku: str, region: str) -> list[dict]:
    query = urllib.parse.urlencode({
        # The preview API version is the one that returns savings-plan prices.
        "api-version": "2023-01-01-preview",
        "$filter": f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' "
                   f"and armSkuName eq '{sku}'",
    })
    with urllib.request.urlopen(f"{API}?{query}", timeout=30) as response:
        items = json.load(response)["Items"]
    return [i for i in items if "Windows" not in i["productName"]]


def options(items: list[dict]) -> list[tuple[str, float]]:
    rows = []
    for item in items:
        price, meter = item["retailPrice"], item["meterName"]
        if item["type"] == "Consumption":
            if meter.endswith("Spot"):
                rows.append(("Spot (evictable)", price))
            elif meter.endswith("Low Priority"):
                continue
            else:
                rows.append(("Pay-as-you-go", price))
                for plan in item.get("savingsPlan", []):
                    rows.append((f"Savings plan, {plan['term']}", plan["retailPrice"]))
        elif item["type"] == "Reservation":
            years = int(item["reservationTerm"].split()[0])
            # Reservation prices are the total for the whole term, not per hour.
            rows.append((f"Reservation, {item['reservationTerm']}",
                         price / (years * 365 * 24)))
    return rows


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: vm_price_options.py <armSkuName> <region>")
    sku, region = sys.argv[1], sys.argv[2]

    rows = options(fetch(sku, region))
    payg = next((p for name, p in rows if name == "Pay-as-you-go"), None)
    if payg is None:
        sys.exit(f"No Linux price found for {sku} in {region}. Check the spelling of both.")

    print(f"{sku} · Linux · {region} · USD list price\n")
    print(f"{'Option':26}{'USD/hour':>10}{'USD/month':>12}{'vs PAYG':>10}")
    for name, hourly in sorted(rows, key=lambda r: -r[1]):
        saving = f"-{(1 - hourly / payg) * 100:.0f}%" if hourly < payg else ""
        print(f"{name:26}{hourly:>10.4f}{hourly * HOURS_PER_MONTH:>12.2f}{saving:>10}")


if __name__ == "__main__":
    main()
