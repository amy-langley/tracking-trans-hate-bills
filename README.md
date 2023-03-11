# Tracking Trans Hate Bills

This repository is my workspace for investigating anti-trans legislation proposed in the US in 2023.

This repository is not intended to identify these bills, which is a task whose scope exceeds my grasp. Instead, I am using two lists that are actively being compiled by other organizations: the ACLU and trackingtranslegislation.com.

* [Mapping Attacks on LGBTQ Rights in U.S. State Legislatures | American Civil Liberties Union](https://www.aclu.org/legislative-attacks-on-lgbtq-rights?state)
* [2023 Anti-Trans Bills | Track Trans Legislation](https://www.tracktranslegislation.com)

There are some rudimentary visualizations in [aclu.ipynb](aclu.ipynb) but the bulk of my effort has been in scripts that download the actual contents of these bills. The trackingtranslegislation.com data includes ids related to Legiscan, a clearing house for legal documentation, and so I have provided [legiscan_retrieve_legislation.ipynb](legiscan_retrieve_legislation.ipynb) to download those from JSON data scraped from TTL's site. There is no host associated with the ACLU data, but I can infer some of the data locations anyways from other link data they provide to various states' own systems. This script can be found at [aclu_retrieve_legislation.ipynb](aclu_retrieve_legislation.ipynb).

An archive of the data I retrieved from the Legiscan API can be found in [legiscan_archive/](legiscan_archive/). This is divided into bills, which contains the actual bills, and tmp, which contains various metadata used in the process of retrieving the bill contents.

To get started with this project, you'll want to have `poetry` and Python 3.9.10 (we recommend pyenv) already installed. Clone the repository and then use `poetry` to install the packages used here. I recommend the `poetry` plugin `poetry-dotenv-plugin` for handling the environment variables for accessing the Legiscan API.

```shell
$ poetry install
$ poetry self add poetry-dotenv-plugin
$ cp env-template .env
```

If you wish to consume the Legiscan API, you'll need to sign up at [https://legiscan.com/user/register](https://legiscan.com/user/register). Once you do, you can create an API key. Put your username, password, and API key in the .env file; note that this file is excluded from git for security. Once your setup is done, start `jupyter lab` and dig in:

```shell
$ poetry run jupyter lab
```

Note that if you change your `.env` you'll need to respawn your jupyter lab server, as it only parses environment variables out of that file at startup.
