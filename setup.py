from setuptools import find_packages, setup

setup_params = dict(
    name='unified',
    use_scm_version=True,
    include_package_data=True,
    packages=find_packages(),
    url='https://github.com/dmonroy/unified',
    author='Darwin Monroy',
    author_email='contact@darwinmonroy.com',
    description='Unified docker API access',
    install_requires=[
        'chilero>=0.3.12'
    ],
    setup_requires=[
        'setuptools_scm',
    ],
)


if __name__ == '__main__':
    setup(**setup_params)
