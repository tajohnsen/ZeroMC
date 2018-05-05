import display
import publisher
import unittest
import threading
import tempfile
import os
import time
import zmq


class TestDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        port = 5555
        cls.context = zmq.Context()
        cls.publisher = dict(socket=cls.context.socket(zmq.PUB))
        cls.publisher["socket"].bind("tcp://*:{}".format(port))

    def test_init(self):
        disp = display.Display("tcp", "localhost", 5555)
        self.assertIsNone(disp.context)
        self.assertIsNone(disp.socket)
        self.assertEqual(disp.protocol, "tcp")
        self.assertEqual(disp.host, "localhost")
        self.assertEqual(disp.port, 5555)
        disp.close()

    def test_connect_and_receive(self):
        disp = display.Display("tcp", "127.0.0.1", 5555)
        with tempfile.TemporaryDirectory() as temp_dir, \
                tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as temp_file:
            temp_file_name = temp_file.name
            temp_file.close()
            disp.file_path = temp_dir
            disp.connect()
            disp_thread = threading.Thread(target=disp.receive_image, kwargs={'file_name': temp_file_name})
            disp_thread.start()
            time.sleep(1)
            self.publisher["socket"].send_multipart([b"0MC", b'', b'abc123'])
            disp_thread.join()
            with open(os.path.join(temp_dir, temp_file_name)) as _file:
                self.assertEqual("abc123", _file.read())
        disp.close()

    @unittest.skip('Too much')
    def test_display_jpeg(self):
        disp = display.Display("tcp", "127.0.0.1", 5555)
        disp.file_path = os.path.dirname(os.path.abspath(__file__))
        disp.display_files()


class TestPublisher(unittest.TestCase):
    def test_init(self):
        pub = publisher.Publisher("tcp", '*', '5555')
        self.assertEqual(pub.protocol, 'tcp')
        self.assertEqual(pub.host, '*')
        self.assertEqual(pub.port, '5555')
        self.assertIsNone(pub.file_path)
        self.assertEqual(pub.timeout, 15)
        self.assertEqual(pub.name, b"0MC")

    def test_send_file(self):
        pub = publisher.Publisher("tcp", '*', '5556')
        disp = display.Display("tcp", "127.0.0.1", 5556)
        with tempfile.TemporaryDirectory() as temp_dir:
            disp.file_path = temp_dir
            print('connecting')
            pub.bind()
            disp.connect()
            print('starting thread')
            disp_thread = threading.Thread(target=disp.receive_image, kwargs={'file_name': 'test.jpg'})
            disp_thread.start()
            print('thread started')
            pub.file_path = os.path.abspath('.')
            print(pub.file_path)
            pub.timeout = 1
            print("starting thread")
            threading.Thread(target=pub.publish, args=[]).start()
            print("thread started")
            print('joining thread')
            disp_thread.join()
            pub.running = False
            print('thread is done')
            with open(os.path.join(temp_dir, 'test.jpg'), 'rb') as in_file, open(
                    os.path.join(os.path.abspath('.'), 'test.jpg'), 'rb') as out_file:
                self.assertEqual(in_file.read(), out_file.read())
