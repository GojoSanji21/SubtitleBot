from datetime import datetime

class Subscription:
    def __init__(self, user_id, subscription_type, start_date, end_date):
        self.user_id = user_id
        self.subscription_type = subscription_type
        self.start_date = start_date
        self.end_date = end_date

    def is_active(self):
        return self.end_date > datetime.now()