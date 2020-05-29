from googletrans import Translator
import collections
import smtplib
import ssl


def translateData(data):
    """
    function to translate non english data in object into english
    :param data: object
    :return: translated object
    """
    translator = Translator()
    for key in data:
        if type(data[key]) == str:
            try:
                data[key] = translator.translate(data[key]).text
            except:
                continue
    return data


class Graph:
    """
    class to define undirected unweighted graph
    """

    def __init__(self):
        self.graph = collections.defaultdict(set)
        self.vertices = set()

    def add(self, u, v):
        self.vertices.add(u)
        self.vertices.add(v)
        self.graph[u].add(v)
        self.graph[v].add(u)


def send_mail(receiver_email, message):
    """
    function to send mail to a specific email address.
    :param receiver_email: the receiver email address.
    :param message: the message to send.
    :return:
    """

    sender_mail = 'PartnerFinderAlerts@gmail.com'
    password = 'Alerts_123'
    ssl_port = 465
    smtp_server = 'smtp.gmail.com'

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, ssl_port, context=context) as server:
            server.login(sender_mail, password)
            server.sendmail(sender_mail, receiver_email, message.as_string())
        print("SENT")
    except Exception as e:
        print("ERROR", e)