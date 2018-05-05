from setuptools import setup

setup(
    name='ZeroMC',
    version='0.1',
    packages=['zeromc'],
    url='https://github.com/tajohnsen/ZeroMC',
    license='MIT',
    author='Tim Johnsen',
    author_email='timothyjohnsen@outlook.com',
    description='0MQ PUB/SUB system where subscribers receive images and display them fullscreen.',
    install_requires=['pyzmq', 'pygame'],
    include_package_data=True
)
