class Display(object):
    """
    Using PUB/SUB 0MQ, receive a PDF or PDFs to display on a screen.
    """
    running: bool

    def __init__(self, protocol, host, port):
        """
        Subscribe to a ZMQ publisher to receive images to display.
        :param protocol: String. ZMQ Protocol.
        :param host: String. Host IP or hostname.
        :param port: Int or String. Port number to use.
        """
        import tempfile
        self.protocol = protocol
        self.host = host
        self.port = port
        self._file_path = tempfile.TemporaryDirectory()
        self.socket = None
        self.context = None
        self.poller = None
        self.running = True

    @property
    def file_path(self):
        import tempfile
        import os
        if isinstance(self._file_path, tempfile.TemporaryDirectory):
            return os.path.abspath(self._file_path.name) + os.sep
        else:
            return os.path.abspath(self._file_path) + os.sep

    @file_path.setter
    def file_path(self, value):
        import tempfile
        import os
        if isinstance(self._file_path, tempfile.TemporaryDirectory):
            self._file_path.cleanup()
        if isinstance(value, str):
            self._file_path = os.path.abspath(value)
        self._file_path = value

    def connect(self):
        import zmq
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"0MC")
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.socket.connect("{s.protocol}://{s.host}:{s.port}".format(s=self))

    def close(self):
        import tempfile
        if isinstance(self._file_path, tempfile.TemporaryDirectory):
            self._file_path.cleanup()

    def display_files(self):
        """
        Display JPG to screen.
        """
        import pygame
        import sys
        import time
        import glob
        import random
        from decimal import Decimal
        from pygame.locals import QUIT, KEYDOWN, K_n, K_f, K_x, K_ESCAPE

        # MAXIMUM picture display sizes
        max_width = 1920
        max_height = 1080

        # display time in seconds
        display = 20

        # randomise pictures, 0 = NO, 1 = YES
        pic_rand = 1

        # Normal or Fullscreen, 0 = normal, 1 = fullscreen
        full_screen = 1

        # Stretch small images to MAXIMUM display size, 0 = NO, 1 = YES
        stretch = 0

        while True:
            # find .jpg files in directory
            pic_list = glob.glob(self.file_path + '*.jpg') + glob.glob(self.file_path + '*.JPG')
            num_pics = len(pic_list)

            for num in range(0, num_pics):
                if pic_rand == 0:
                    image_file = pic_list[num]
                else:
                    image_file = pic_list[int(random.random() * num_pics)]
                image = pygame.image.load(image_file)
                size = image.get_rect()
                width = size[2]
                height = size[3]
                if width < max_width and stretch == 1:
                    height = height * (Decimal(max_width) / Decimal(width))
                    width = max_width
                    image = pygame.transform.scale(image, (width, height))
                if height < max_height and stretch == 1:
                    width = width * (Decimal(max_height) / Decimal(height))
                    height = max_height
                    image = pygame.transform.scale(image, (width, height))
                if width > max_width:
                    height = height * (Decimal(max_width) / Decimal(width))
                    width = max_width
                    image = pygame.transform.scale(image, (width, height))
                if height > max_height:
                    width = width * (Decimal(max_height) / Decimal(height))
                    height = max_height
                    image = pygame.transform.scale(image, (width, height))
                if full_screen == 1:
                    window_surface_object = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                else:
                    window_surface_object = pygame.display.set_mode((width, height))
                    pygame.display.set_caption('Slideshow')
                window_surface_object.blit(image, (0, 0))
                pygame.display.update()
                t = time.time()
                while t > time.time() - display:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()

                        elif event.type == KEYDOWN:
                            # press N for normal screen
                            if event.key == K_n:
                                window_surface_object = pygame.display.set_mode((width, height))
                                window_surface_object.blit(image, (0, 0))
                                pygame.display.update()
                                full_screen = 0
                            # press F for full screen
                            if event.key == K_f:
                                window_surface_object = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                                window_surface_object.blit(image, (0, 0))
                                pygame.display.update()
                                full_screen = 1
                            # press X to EXIT
                            if event.key == K_x or event.key == K_ESCAPE:
                                pygame.quit()
                                self.running = False
                                sys.exit()

            time.sleep(20)

    def _new_file(self, data):
        import glob
        for file in glob.glob(self.file_path + '*.jpg'):
            with open(file, 'rb') as in_file:
                if data == in_file.read():
                    return False
        return True

    def receive_image(self, file_name=None):
        """
        Receive image via ZMQ
        """
        import tempfile
        import os
        import zmq

        print('waiting to receive')
        socks = dict(self.poller.poll(10000))
        if socks.get(self.socket) == zmq.POLLIN:
            sub, _, data = self.socket.recv_multipart()
            if not self._new_file(data):
                # file already exists, do nothing
                return
            print('got new data')
            if file_name is not None:
                print('saving to {}'.format(os.path.join(self.file_path, file_name)))
                with open(os.path.join(self.file_path, file_name), 'wb') as image_file:
                    image_file.write(data)
            else:
                print('saving')
                with tempfile.NamedTemporaryFile(dir=self.file_path, delete=False, suffix='.jpg') as image_file:
                    print('saving to {}'.format(image_file.name))
                    image_file.write(data)
        else:
            # if timeout, reconnect
            self.socket.connect("{s.protocol}://{s.host}:{s.port}".format(s=self))

    def run(self):
        import threading

        display_thread = threading.Thread(target=self.display_files, args=[])
        display_thread.start()

        self.connect()
        while self.running:
            self.receive_image()


def run_display():
    display = Display('tcp', 'localhost', 5678)
    display.run()


if __name__ == '__main__':
    run_display()
