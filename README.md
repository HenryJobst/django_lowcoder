<h1 align="center">
  <a href="https://github.com/HenryJobst/django_lowcoder/issues">
    <img src="https://github.com/HenryJobst/django_lowcoder/docs/images/logo.svg" alt="Logo" width="125" height="125">
  </a>
</h1>

<div align="center">
  Django LowCoder - Create Web-Applications out of spreadsheets (e.g. Excel/CSV-Tables)!
  <br />
  <br />
  <a href="https://github.com/HenryJobst/django_lowcoder/issues/new?assignees=&labels=bug&template=01_BUG_REPORT.md&title=bug%3A+">Report a Bug</a>
  ·
  <a href="https://github.com/HenryJobst/django_lowcoder/issues/new?assignees=&labels=enhancement&template=02_FEATURE_REQUEST.md&title=feat%3A+">Request a Feature</a>
  .
  <a href="https://github.com/HenryJobst/django_lowcoder/discussions">Ask a Question</a>
</div>

<div align="center">
<br />

[![license](https://img.shields.io/github/license/HenryJobst/django_lowcoder.svg?style=flat-square)](LICENSE)

[![PRs welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg?style=flat-square)](https://github.com/HenryJobst/django_lowcoder/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
[![made with hearth by HenryJobst](https://img.shields.io/badge/made%20with%20%E2%99%A5%20by-HenryJobst-ff1414.svg?style=flat-square)](https://github.com/HenryJobst)

</div>

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Cookiecutter template](#cookiecutter-template)
    - [Manual setup](#manual-setup)
    - [Variables reference](#variables-reference)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)
- [Acknowledgements](#acknowledgements)

</details>

---

## About

<table>
<tr>
<td>

Do you want produce a web application with [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) 
functionality out of existing [Spreadsheet](https://en.wikipedia.org/wiki/Spreadsheet) files (e.g. Excel, CSV), 
then this project can help you.

With the power of Django, Panda and Cookiecutter you will fast get a new web application, to work with.  

Key features of **Django LowCode** (*) - not fully implemented or planned feature:

- Configurable Use of existing Cookiecutter Code Templates for project generation
- Configurable Import of Excel-Files to build initial table models (automatic data type and foreign key deduction) (*) 
- Configurable Table und Column configurations (including relations between tables)
- Configurable Application Generation (*) 
- Configurable Deployment Types for the generated applications (*)
- Localizable Web-UI (English & German available so far)

<details open>
<summary>Additional info</summary>
<br>

This project start with the interest to learn the python django web framework. The original motivation 
was, to use the power of django to rapidly build a new django web apps for imported spreadsheet data with basic CRUD 
operations. 

</details>

</td>
</tr>
</table>

### Built With

- [Django](https://www.djangoproject.com/)
- [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms)
- [crispy-bootstrap5](https://github.com/django-crispy-forms/crispy-bootstrap5)
- [Pandas](https://pandas.pydata.org/)
- [Bootstrap](https://getbootstrap.com/)
- [htmx](https://htmx.org/)
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter)
- [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django)

## Getting Started

### Prerequisites

This project is a python django project. So you need at least a actual python interpreter to run this project.

### Usage

...

#### Manual setup

...

#### Variables reference

...

## Roadmap

See the [open issues](https://github.com/HenryJobst/django_lowcoder/issues) for a list of proposed features (and known issues).

- [Top Feature Requests](https://github.com/HenryJobst/django_lowcoder/issues?q=label%3Aenhancement+is%3Aopen+sort%3Areactions-%2B1-desc) (Add your votes using the 👍 reaction)
- [Top Bugs](https://github.com/HenryJobst/django_lowcoder/issues?q=is%3Aissue+is%3Aopen+label%3Abug+sort%3Areactions-%2B1-desc) (Add your votes using the 👍 reaction)
- [Newest Bugs](https://github.com/HenryJobst/django_lowcoder/issues?q=is%3Aopen+is%3Aissue+label%3Abug)

## Contributing

First off, thanks for taking the time to contribute! Contributions are what makes the open-source community such an amazing place to learn, inspire, and create. Any contributions you make will benefit everybody else and are **greatly appreciated**.

Please try to create bug reports that are:

- _Reproducible._ Include steps to reproduce the problem.
- _Specific._ Include as much detail as possible: which version, what environment, etc.
- _Unique._ Do not duplicate existing opened issues.
- _Scoped to a Single Bug._ One bug per report.

Please adhere to this project's [code of conduct](docs/CODE_OF_CONDUCT.md).

You can use [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) to check for common markdown style inconsistency.

## Support

Reach out to the maintainer at one of the following places:

- [GitHub discussions](https://github.com/HenryJobst/django_lowcoder/discussions)
- The email which is located [in GitHub profile](https://github.com/HenryJobst)

## License

This project is licensed under the **MIT license**. Feel free to edit and distribute this template as you like.

See [LICENSE](LICENSE) for more information.

## Acknowledgements

Thanks for these awesome resources that were used during the development of the **Django LowCoder**:

- <https://github.com/johncmacy/django-from-excel>
- <https://github.com/cjolowicz/cookiecutter-hypermodern-python>
- <https://github.com/dec0dOS/amazing-github-template>
