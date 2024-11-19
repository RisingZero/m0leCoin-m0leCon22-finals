import requests

class Mailbox():
    def __init__(self, url):
        self.url = url


    def get_mails(self, box: str):
        res = requests.get(f'{self.url}/{box}')
        assert res.status_code == 200
        return res.text


    def send_mails(self, box: str, msg: str):
        res = requests.post(f'{self.url}/{box}', data=msg)
        assert res.status_code == 200