# Script to delete tagged docker images.
# Usage: <package_name> <tag> <github_token>
#


import requests


def get_package_versions(package_name, package_type):
    print("get_package_versions", package_name, package_type)
    # https://docs.github.com/en/rest/reference/packages#get-all-package-versions-for-a-package-owned-by-the-authenticated-user
    result = []
    done = False
    page = 1

    while not done:
        response = session.get(f"https://api.github.com/user/packages/{package_type}/{package_name}/versions", params={"per_page" : 100, "page": page})
        response.raise_for_status()
        json = response.json()
        result.extend(json)
        done = len(json) != 100
        page += 1

    return result


def delete_package_version(package_name, package_type, id):
    print("delete_package_version", package_name, package_type, id)

    # https://docs.github.com/en/rest/reference/packages#delete-a-package-version-for-the-authenticated-user
    response = session.delete(f"https://api.github.com/user/packages/{package_type}/{package_name}/versions/{id}")
    response.raise_for_status()


def get_tagged_container(package_name, tag):
    print("get_tagged_container", package_name, tag)
    packages = get_package_versions(package_name, "container")
    return [version for version in packages if tag in version["metadata"]["container"]["tags"]]


def delete_tagged_container(package_name, tag):
    print("delete_tagged_container", package_name, tag)
    tags = get_tagged_container(package_name, tag)

    if tags:
        for tag in tags:
            delete_package_version(package_name, "container", tag["id"])
    else:
        raise Exception(f"No containers to delete: {package_name} {tag}")


################################

import sys

if len(sys.argv) != 4:
    raise SystemExit("Usage: docker-cleanup.py <package_name> <tag> <github_token>")

package_name = sys.argv[1]
tag = sys.argv[2]
token = sys.argv[3]

print("package_name = ", package_name)
print("tag = ", tag)

session = requests.Session()
session.headers.update({"Authorization": f"token {token}", "Accept" : "application/vnd.github.v3+json"})
delete_tagged_container(package_name, tag)

