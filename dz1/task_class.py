from datetime import datetime, date, timedelta
from wsgiref.simple_server import make_server
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class Task:
    def __init__(self, title, estimate, state='in_progress'):
        self.title = title
        self.estimate = estimate
        if state == 'in_progress':
            self._state = 'in_progress'
        else:
            self._state = 'ready'

    state = property()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value == 'in_progress':
            self._state = 'in_progress'
        else:
            self._state = 'ready'

    is_failed = property()

    @property
    def is_failed(self):
        return True if self._state == 'in_progress' and self.estimate < datetime.now() else False

    @property
    def remaining(self):
        return self.estimate - datetime.now() if self._state == 'in_progress' else 0

    def ready(self):
        self._state = 'ready'


class Roadmap:
    def __init__(self, tasks=[]):
        self.tasks = tasks

    @property
    def today(self):
        return [item for item in self.tasks if item.estimate.date() == date.today()]  # сравниваем только по датам

    def filter(self, state):
        return [item for item in self.tasks if item.state == state]

    def critical(self):
        return [item for item in self.tasks if (item.estimate - date.today()) < timedelta(days=3)]


def WsgiApp(environment, start_response_callback):
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
    ]
    answer = ''
    tasks =[]
    # по условию необходимо использовать класс Task
    for item in get_dataset('dataset.yml'):
        current_task = Task(item[0], item[2], item[1])  # в соответствии с порядком
        tasks.append(current_task)
    all_task = Roadmap(tasks)

    for item in all_task.critical():
        answer += item.title + ', ' + item.estimate.isoformat() + '<br>'

    start_response_callback('200 OK', response_headers)
    return [
        answer.encode('utf-8'),
    ]


def get_dataset(filename):
    with open(filename, 'rt', encoding='utf-8') as input:
        package = load(input, Loader=Loader)
        dataset = package.get('dataset')
        if not isinstance(dataset, list):
            raise ValueError('wrong format')
        yield from dataset

http_server = make_server('127.0.0.1', 8080, WsgiApp)
http_server.serve_forever()