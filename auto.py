import json
import time

import schedule

from order import order_stadium

if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)

    schedule.every().day.at(config["auto"]["time"]).do(order_stadium, config)

    while True:
        schedule.run_pending()
        time.sleep(1)
