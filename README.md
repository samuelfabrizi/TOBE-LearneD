<div id="top"></div>

[![MIT License][license-shield]][license-url]

# Decentralized-SmartGrid-ML

<!-- TABLE OF CONTENTS -->
<details>
   <summary>Table of Contents</summary>
   <ul>
      <li>
         <a href="#getting-started">Getting Started</a>
         <ul>
            <li><a href="#installation">Installation</a></li>
            <li><a href="#requirements">Requirements</a></li>
            <li><a href="#coverage-and-linting">Coverage and Linting</a></li>
         </ul>
      </li>
      <li><a href="#license">License</a></li>
      <li><a href="#contact">Contact</a></li>
   </ul>
</details>

## Getting Started

[![Python language][python-shield]][python-url] 
[![Javascript language][javascript-shield]][javascript-url]
[![Solidity language][solidity-shield]][solidity-url]

### Installation

---
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

---
Define the following environment variables:
- _BC_ADDRESS_: blockchain address (for Ganache use 127.0.0.1:7545)\

⚠  **If you want to use a different blockchain** remember to change the _BC_ADDRESS_ environment variable

### Coverage and Linting

---
![Coverage][coverage-shield]\
If you want to run the coverage test and the linting for the whole framework you can run respectively:\
`sh coverage_test.sh` and `sh linter_script.sh`

In order to execute and see the output of the Smart Contract tests, you can execute `truffle test`

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.



## Contact

[![LinkedIn][linkedin-shield]][linkedin-url]
[![Twitter][twitter-shield]][twitter-url]
[![Gmail][gmail-shield]][gmail-url]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-shield]: https://img.shields.io/badge/LICENSE-MIT-green?style=for-the-badge
[license-url]: https://github.com/samuelfabrizi/Decentralized-SmartGrid-ML/blob/develop/LICENSE
[coverage-shield]: .badges/python_coverage_badge.svg
[python-shield]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=darkgreen
[python-url]: https://www.python.org/
[javascript-shield]: https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E
[javascript-url]: https://www.javascript.com/ 
[solidity-shield]: https://img.shields.io/badge/Solidity-e6e6e6?style=for-the-badge&logo=solidity&logoColor=black
[solidity-url]: https://docs.soliditylang.org/
[gmail-shield]: https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white
[mail-url]: mailto:samuel.fabrizi97@gmail.com
[linkedin-shield]: https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://www.linkedin.com/in/samuel-fabrizi/
[twitter-shield]: https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white
[twitter-url]: https://twitter.com/SamuelFabrizi
[gmail-shield]: https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white 
[gmail-url]: mailto:samuel.fabrizi97@gmail.com