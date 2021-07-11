import arrow


class CandlePeriods:
    MIN = 'min'
    TWO_MIN = 'two_min'
    FIVE_MIN = 'five_min'
    TEN_MIN = 'ten_min'
    FIFTEEN_MIN = 'fifteen_min'


class Candles(object):
    def __init__(self, candles, start_time=None):
        self.candles = candles
        # For filtering out irrelevant candles
        if start_time:
            self.candles = self.__slice_by_time(start_time)

    def __slice_by_time(self, start_time):
        for index, candle in enumerate(self.candles):
            if arrow.get(candle['datetime']) >= arrow.get(start_time):
                return self.candles[index - 1:]

        raise ValueError(f"None of the candles match start_time: {start_time}")

    def get_percentage_by_period(self, period):
        if period == CandlePeriods.MIN:
            return 100 * (self.candles[1]['close'] / self.candles[0]['close'])


