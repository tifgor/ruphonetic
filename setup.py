from setuptools import setup, find_packages
from pathlib import Path

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 11',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
 
setup(
  name='ruphonetic',
  version='0.2.1',
  description='Russian Phonetic Analysis Module',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='', 
  author='Igor Furkalo',
  author_email='igor.furkalo@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='quantanalysis', 
  packages=find_packages(),
  include_package_data=True,
  package_data={
      'ruphonetic': ['accentuation/*.dat'],
  },
  install_requires=['numpy==1.26.4', 'spacy==3.3.0', 'matplotlib==3.5.2'],
)





