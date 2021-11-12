<div id="top"></div>

[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

# Decentralized-SmartGrid-ML

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#correctness">Correctness</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


## Getting Started

### Installation
1. Create a Python 3 virtual environment with\
`virtualenv -p pyton3 bcai_venv`

2. Activate the Python virtual environment
    ```sh
    source bcai_venv/bin/activate
    ```

3. Install [Truffle](https://trufflesuite.com/truffle)
    ```sh
    npm install -g truffle
    ```

4. [Install Ganache](https://www.trufflesuite.com/ganache)

5. Clone the repo 
    ```sh
    # if you use https
    git clone https://github.com/samuelfabrizi/Decentralized-SmartGrid-ML.git
    # if you use ssh
    git@github.com:samuelfabrizi/Decentralized-SmartGrid-ML.git
    ```
   
6. Install the requirements with
    ```sh
    pip install -r requirements/requirements.txt
    npm install
    ```

### Requirements
Define the following environment variables:
- _BC_ADDRESS_: blockchain address (for Ganache use 127.0.0.1:7545)\
⚠  **If you want to use a different blockchain** remember to change the _BC_ADDRESS_ environment variable

### Correctness
If you want to run the coverage test and the linting for the whole framework you can run respectively:\
`sh coverage_test.sh` and `sh linter_script.sh`

In order to execute and see the output of the Smart Contract tests, you can execute `truffle test`

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-shield]: https://img.shields.io/badge/LICENSE-MIT-green?style=for-the-badge
[license-url]: https://github.com/samuelfabrizi/Decentralized-SmartGrid-ML/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/samuel-fabrizi/
