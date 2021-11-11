# action-cleanup-package

This is a GitHub Action to delete GitHub packages.  It is very useful to clean up unneeded Docker 
images in the GitHub Container Registry (ghcr.io) after a PR is closed. 

The example below removes Docker images in ghcr.io with the specified package name and tag.  Here, `github-token`
is set to a secret, `CI_ACTION_TOKEN`, which is a personal access token with package deletion permissions.

```
# Delete Docker images after PR merge
#

name: 'Clean up Docker images from PR'

on:
  pull_request:
    types: [closed]

jobs:
  purge-image:
    name: Delete image from ghcr.io
    runs-on: ubuntu-latest
    steps:
      - uses: chipkent/action-cleanup-package@v1.0.1
        with:
          package-name: ${{ github.event.repository.name }}
          tag: pr-${{ github.event.pull_request.number }}
          github-token: ${{ secrets.CI_ACTION_TOKEN }}
```
