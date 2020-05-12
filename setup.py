import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tcp_probe", # Replace with your own username
    version="0.0.3",
    author="Bruce Spang",
    author_email="bruce@brucespang.com",
    description="Tools for tracing TCP in Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brucespang/tcp_probe",
    packages=setuptools.find_packages(),
    install_requires=[
        'Click',
        'lark',
        # technically yes, but creates annoying dependency issues on servers...
        # 'pandas'
        # 'plorts'
        # 'matplotlib'
        # 'numpy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Operating System Kernels :: Linux",
        "Topic :: System :: Networking :: Monitoring"
    ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            "tcp_probe = tcp_probe.cli:cli",
        ]
    }
)
