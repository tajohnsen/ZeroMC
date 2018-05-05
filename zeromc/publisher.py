class Publisher(object):
    running: bool

    def __init__(self, protocol, host, port, **kwargs):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.file_path = kwargs.get('file_path')
        self.timeout = kwargs.get('timeout', 15)
        self.name = kwargs.get('name', b"0MC")
        self.running = True
        self.socket = None
        self.published = dict()

    def _verify_settings(self):
        import os
        assert self.file_path is not None, "Path not set. Cannot publish if I don't know where to get images."
        assert os.path.exists(os.path.abspath(self.file_path)), "Path given does not exist. ({})".format(self.file_path)

    def bind(self):
        import zmq
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("{s.protocol}://{s.host}:{s.port}".format(s=self))

    def publish(self):
        import os
        self._verify_settings()
        for directory, _, files in os.walk(os.path.abspath(self.file_path)):
            if not self.running:
                break
            for file in files:
                if not self.running:
                    break
                if 'jpg' in file.lower():
                    print('sending {}'.format(file))
                    with open(os.path.join(self.file_path, directory, file), 'rb') as image_file:
                        self.socket.send_multipart([self.name, b'', image_file.read()])

    def run(self):
        import time
        self.bind()
        while True:
            self.publish()
            time.sleep(self.timeout)


def run_publisher():
    import os
    publisher = Publisher('tcp', '*', 5678)
    publisher.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'tests'))
    publisher.run()


if __name__ == '__main__':
    run_publisher()
