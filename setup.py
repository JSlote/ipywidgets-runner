import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="ipywidgets-runner",
	version="0.0.1",
	author="Joseph Slote", # Corresponding author
	author_email="joseph.slote@gmail.com",
	description="A lazy function runner for ipywidgets dashboards",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="http://github.com/JSlote/ipywidgets-runner",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	],
	python_requires='>=3.6'
)