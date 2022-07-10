# Script to delete tagged docker images.
# Usage: <package_name> <tag> <github_token>
#


import requests


def get_package_versions(package_name, package_type, org):
    print("get_package_versions", package_name, package_type, org)
    result = []
    done = False
    page = 1

    if org:
        # https://docs.github.com/en/rest/packages#list-packages-for-an-organization=
        package_url = f"https://api.github.com/orgs/{org}/packages/{package_type}/{package_name}/versions"
    else:
        # https://docs.github.com/en/rest/reference/packages#get-all-package-versions-for-a-package-owned-by-the-authenticated-user
        package_url = f"https://api.github.com/user/packages/{package_type}/{package_name}/versions"

    while not done:
        response = session.get(package_url, params={"per_page" : 100, "page": page})
        response.raise_for_status()
        json = response.json()
        result.extend(json)
        done = len(json) != 100
        page += 1

    return result


def delete_package_version(package_name, package_type, id, org):
    print("delete_package_version", package_name, package_type, id, org)
    
    if org:
        # https://docs.github.com/en/rest/packages#delete-package-version-for-an-organization=
        delete_url = f"https://api.github.com/orgs/{org}/packages/{package_type}/{package_name}/versions/{id}"
    else:
        # https://docs.github.com/en/rest/reference/packages#delete-a-package-version-for-the-authenticated-user
        delete_url = f"https://api.github.com/user/packages/{package_type}/{package_name}/versions/{id}"
    response = session.delete(delete_url)
    response.raise_for_status()


def get_tagged_container(package_name, tag, org):
    print("get_tagged_container", package_name, tag, org)
    packages = get_package_versions(package_name, "container", org)
    return [version for version in packages if tag in version["metadata"]["container"]["tags"]]


def delete_tagged_container(package_name, tag, org):
    print("delete_tagged_container", package_name, tag, org)
    tags = get_tagged_container(package_name, tag, org)

    if tags:
        for tag in tags:
            delete_package_version(package_name, "container", tag["id"], org)
    else:
        raise Exception(f"No containers to delete: {package_name} {tag}")    


################################

import sys

if len(sys.argv) < 4 or len(sys.argv) > 5:
    raise SystemExit(f"Usage: docker-cleanup.py <package_name> <tag> <github_token> <github-org (optional)>\nArgs: {sys.argv}")

package_name = sys.argv[1]
tag = sys.argv[2]
token = sys.argv[3]

org = None
if len(sys.argv) == 5:
    org = sys.argv[4]

print("package_name = ", package_name)
print("tag = ", tag)
print("org = ", org)

session = requests.Session()
session.headers.update({"Authorization": f"token {token}", "Accept" : "application/vnd.github.v3+json"})
delete_tagged_container(package_name, tag, org)
