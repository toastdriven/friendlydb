from distutils.core import setup

setup(
    name = "friendlydb",
    version = "2.0.0",
    description = "A small & fast following/followers database.",
    author = 'Daniel Lindsley',
    author_email = 'daniel@toastdriven.com',
    long_description=open('README.rst', 'r').read(),
    packages=[
        'friendlydb',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    url = 'http://github.com/toastdriven/friendlydb',
    install_requires=[
        'redis>=2.72',
    ],
)
