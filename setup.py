from setuptools import setup,find_packages

setup(name='molSimplify',version="v1.1-alpha",packages=find_packages(),
      include_package_data = True,
      entry_points={'console_scripts': ['molsimplify = molSimplify.__main__:main']},
      )