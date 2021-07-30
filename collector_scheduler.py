# !/usr/bin/env python3
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from google.cloud import pubsub_v1

from lighweight_runnable import LightRunnable


class CollectScheduler(LightRunnable):
    PUBSUB_TICKERS_TOPIC_NAME = "projects/stocker-300519/topics/collector-tickers"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.publisher = pubsub_v1.PublisherClient()
        self.topic_name = self.PUBSUB_TICKERS_TOPIC_NAME + '-dev' if self._debug else self.PUBSUB_TICKERS_TOPIC_NAME

    def publish(self):
        self.logger.info("Publishing tickers")
        for ticker in self._tickers_list:
            self.publisher.publish(self.topic_name, ticker.encode('utf-8'))
        self.logger.info("Finished publishing tickers")

    def run(self):
        scheduler = BlockingScheduler()

        market_cron = "* 13-21 * * 1-5"
        non_market_cron = "0 21-23,0-12 * * 0-6"

        self.disable_apscheduler_logs()

        non_market_trigger = CronTrigger.from_crontab(non_market_cron)
        market_trigger = CronTrigger(second="*/30", minute="*", hour="13-21", day="*", year="*", day_of_week="1-5")

        trigger = OrTrigger([market_trigger, non_market_trigger])

        scheduler.add_job(self.publish,
                          trigger=trigger,
                          max_instances=2,
                          misfire_grace_time=120)

        scheduler.start()


def main():
    try:
        if os.getenv('FUNCTION', 'false').lower() == 'false':
            CollectScheduler().run()
        else:
            CollectScheduler().publish()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
    # with open('csv/invalids.json') as remove_file:
    #     import json
    #     tickers_remove = json.load(remove_file)
    #     with open('csv/tickers.csv') as tickers_file:
    #         tickers = tickers_file.read().splitlines()
    #         tickers_removed = [ticker for ticker in tickers if ticker not in tickers_remove]
    #         with open('csv/removed.csv', 'a') as removed_file:
    #             [removed_file.write(ticker+'\n') for ticker in tickers_removed]
