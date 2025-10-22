# ai-tokentrace
Add your description here

## Getting Started

To set up the development environment, you'll need Python 3.9+ and `uv`.

1.  **Install all dependencies and create the virtual environment:**
    ```bash
    uv sync
    ```

`uv` will automatically create a virtual environment in `.venv` if one doesn't exist, and then install all dependencies from `pyproject.toml`.

From here, `uv` will automatically use the virtual environment in this directory. For example, to run a command, use `uv run <command>`.

### Java JRE Setup

Running the integration tests requires a Java JRE to run the Google Cloud emulators. We recommend using [SDKMAN!](https://sdkman.io/) to install and manage Java versions.

1.  **Install SDKMAN!:**
    ```bash
    curl -s "https://get.sdkman.io" | bash
    ```
    Follow the on-screen instructions to complete the installation.

2.  **Install Java:**
    ```bash
    sdk install java
    ```

This will install a suitable version of the Java JRE and make it available in your shell.

See [go/releasing](http://go/releasing) (available externally at
https://opensource.google/documentation/reference/releasing) for more information about
releasing a new Google open source project.

This template uses the Apache license, as is Google's default.  See the
documentation for instructions on using alternate license.

## How to use this template

1. Clone it from GitHub.
    * There is no reason to fork it.
1. Create a new local repository and copy the files from this repo into it.
1. Modify README.md and docs/contributing.md to represent your project, not the
   template project.
1. Develop your new project!

``` shell
git clone https://github.com/google/new-project
mkdir my-new-thing
cd my-new-thing
git init
cp -r ../new-project/* ../new-project/.github .
git add *
git commit -a -m 'Boilerplate for new Google open source project'
```

## Source Code Headers

Every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

Apache header:

    Copyright 2024 Google LLC

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
