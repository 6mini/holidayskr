from setuptools import setup, find_packages

setup(
    name='holidayskr',
    version='0.1.0',
    author='Yoonmin Lee',
    author_email='real6mini@gmail.com',
    packages=find_packages(),
    description='대한민국의 공식 휴일을 계산하는 Python 패키지입니다. 양음력 고정 휴일 뿐 아니라, 매년 변동되는 휴일(대체 공휴일, 선거일 등)까지 포함하여 정확한 휴일 정보를 제공합니다. 금일 혹은 특정 날짜가 휴일인지 확인하거나, 주어진 연도의 모든 휴일을 조회할 수 있습니다.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/6mini/holidayskr',
    license='MIT',
    install_requires=[
        'korean_lunar_calendar>=0.2.1',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'check-manifest',
            'twine',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Scheduling",
    ],
    keywords='Korea holidays lunar-calendar public-holidays',
    python_requires='>=3.6',
)