import requests
import json
import semver
import os


VERSION_PLACEHOLDER = "X.X.X"


def update_setup(new_version):
    with open("setup.py") as f:
        content = f.read()
        if VERSION_PLACEHOLDER not in content:
            raise Exception("setup.py version parameter has been modified")

    with open("setup.py", "w") as f:
        print("changing setup.py version parameter")
        content = content.replace(VERSION_PLACEHOLDER, new_version)
        f.write(content)


def pypi_version(response):
    data = json.loads(response.text)
    if "info" in data:
        return data["info"]["version"]
    else:
        raise Exception(f"Invalid response {data} from pypi. "
                        f"info tag missing")


if __name__ == "__main__":
    tag_ver = os.getenv("TRAVIS_TAG")

    if tag_ver is None:
        raise TypeError("Expected TRAVIS_TAG environment variable to be set")

    # verify tag is valid semver
    semver.parse(tag_ver)

    response = requests.get("https://pypi.org/pypi/haystack-client/json")

    if response.ok:
        old_ver = pypi_version(response)
    elif response.status_code == 404:
        print("must be a new repo")
        old_ver = "0.0.0"
    else:
        raise Exception(f"Failed to get existing version information from pypi."
                        f" Response was {response}")

    if semver.compare(tag_ver, old_ver) > 0:
        print(f"Previouis PyPI version is {old_ver}, updating setup.py with new"
              f" version {tag_ver}")
        update_setup(tag_ver)
    else:
        raise Exception(f"pypi version {old_ver} is newer than tagged version"
                        f" {tag_ver}")
