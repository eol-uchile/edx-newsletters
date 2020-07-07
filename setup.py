import setuptools

setuptools.setup(
    name="edxnewsletters",
    version="0.0.1",
    author="Luis Santana",
    author_email="luis.santana@uchile.cl",
    description="",
    long_description="",
    url="https://eol.uchile.cl",
    packages=setuptools.find_packages(),
    install_requires=["unidecode>=1.1.1"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "lms.djangoapp": ["edxnewsletters = edxnewsletters.apps:EdxNewslettersConfig"]},
)
