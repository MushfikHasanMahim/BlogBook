def get_time(zone='Asia/Dhaka'):
    from datetime import datetime 
    import pytz 
    
    
    def convert(time):
        return time.strftime("%m %B, %Y %I:%m:%p")
    
    
    UTC = pytz.utc
    IST = pytz.timezone(zone) 
    t = datetime.now(IST) 
    return convert(t)
    
def get_time_(zone='Asia/Dhaka'):
    from datetime import datetime 
    import pytz
    UTC = pytz.utc
    IST = pytz.timezone(zone) 
    t = datetime.now(IST) 
    return t

