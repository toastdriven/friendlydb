from distutils.core import setup

setup(
    name = "friendlydb",
    version = "0.4.0",
    description = "A small & fast following/followers database.",
    author = 'Daniel Lindsley',
    author_email = 'daniel@toastdriven.com',
    long_description=open('README.rst', 'r').read(),
    packages=[
        'friendlydb',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    url = 'http://github.com/toastdriven/friendlydb'
)
