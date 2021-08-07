import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rt-hat-inr", # Replace with your own username
    version="0.1.7",
    author="Marian Ulbricht",
    author_email="ulbricht@innoroute.de",
    description="RealtimeHAT control",
    long_description=long_description,
    install_requires=[
   'npyscreen',
   'wget',
   'configobj'   
		],
    scripts=['bin/INR_change_bitstream','bin/INR_FPGA_status','bin/INR_FPGA_license','bin/INR-config'],
    long_description_content_type="text/markdown",
    url="https://github.com/InnoRoute/RealtimeHAT",
    project_urls={
        "Bug Tracker": "https://github.com/InnoRoute/RealtimeHAT/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
