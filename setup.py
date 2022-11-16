import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mojoperception",
    version="2.0.0",
    author="Hoomano",
    author_email="contact@hoomano.com",
    description="Mojo Perception Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://mojo.ai",
    project_urls={
        "Git": "https://github.com/hoomano/mojo-perception-python",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "mediapipe",
        "opencv-python",
        "python-socketio",
        "websocket-client",
        "requests"
    ]
)