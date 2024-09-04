class FOMO_Detector_v0:
    def __init__(self, incr_per, num_days):
        self.incr_per = incr_per
        self.num_days = num_days
        self.buffer_date = []
        self.buffer_value = []

    def process(self, date, value):
        if len(self.buffer_date) > 0:
            time_diff = date-self.buffer_date[0]
            if time_diff.days >= self.num_days:
                old_value = self.buffer_value.pop(0)
                increase = ((value - old_value) / old_value) * 100
                self.buffer_date.pop(0)
                self.buffer_date.append(date)
                self.buffer_value.append(value)
                if increase >= self.incr_per:
                    return True, increase, old_value
                else:
                    return False, increase, old_value

        self.buffer_date.append(date)
        self.buffer_value.append(value)

        return None, None, None
