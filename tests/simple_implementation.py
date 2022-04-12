import time


class OnlineTime:
    def __init__(self, login_time):
        self.login_time = login_time
    
    @property
    def total_time(self):
        return self.get_online_time()

    def get_online_time(self):
        return time.time()-self.login_time
    
    def __call__(self, *args, **kwds):
        # super().__call__(*args, **kwds)
        return self.total_time


class User:
    def __init__(self, **kw):
        self.userData = {}
        
        self._init(**kw)

    def _init(self, **kw):
        login_time = time.time()
        self.userData = {'id':1, 'name':'user_name', 'online_time':OnlineTime(login_time), 'status': 'idle', 'sent_messages':[]}
        self.userData.update(kw)
    
    def send_message(self, message):
        self.userData['sent_messages'].append(message)
    
    def clear_message_history(self):
        self.userData['sent_messages'] = []
