from setuptools import find_packages, setup

setup(
    name='proto-dashboard-taiga',
    description='APIs do AJNA',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-wtf',
        'gunicorn',
        'pandas',
        'psycopg2',
        'sqlalchemy'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite="tests",
    package_data={
    },
    extras_require={
        'dev': [
            'coverage',
            'flake8',
            'flake8-docstrings',
            'flake8-todo',
            'flake8-quotes',
            'isort',
            'pylint',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'radon',
            'tox'
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.5',
    ],
)
