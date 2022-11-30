from setuptools import setup

VERSION = '1.0.0'
DESCRIPTION = 'A Python implementation of Counterfactual Regret Minimization (CFR).'
LONG_DESCRIPTION = 'A Python library for building the game trees of zero-sum imperfect information games and solving ' \
                   'for their Nash equilibrium using Counterfactual Regret Minimization (CFR).'

setup(
    name='openCFR',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/stockhamrexa/OpenCFR',
    author='Rex Stockham',
    author_email='rexstockham13@gmail.com',
    license='MIT',
    python_requires='>=3.7',
    packages=['openCFR', 'openCFR.games', 'openCFR.games.sample_games', 'openCFR.minimizers'],
    package_dir={'openCFR': '.'},
    package_data={'openCFR': ['./pretrained/*', 'LICENSE.txt', 'README.md']},
    include_package_data=True,
    install_requires=['numpy>=1.23.0', 'tqdm>=4.57.0'],
    keywords=[
        'CFR',
        'CFR+',
        'CFR plus',
        'chance sampling',
        'Counterfactual Regret Minimization',
        'game tree',
        'heads-up no-limit',
        'imperfect information',
        'Kuhn',
        'MCCFR',
        'Monte Carlo Counterfactual Regret Minimization',
        'Nash equilibrium',
        'outcome sampling',
        'poker',
        'Python',
        'regret based pruning',
        'rock-paper-scissors',
        'Texas Hold-Em',
        'zero sum',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)