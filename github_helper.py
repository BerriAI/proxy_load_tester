import requests 
import os
import dotenv
from dotenv import load_dotenv
from github import Github
load_dotenv()


def new_stable_release(version):
    print("starting a new stable release for version=", version)
    commit_hash = get_release_commit_hash(version)
    """
    Send
    curl -X POST \
              -H "Accept: application/vnd.github.v3+json" \
              -H "Authorization: Bearer $GITHUB_TOKEN" \
              "https://api.github.com/repos/BerriAI/litellm/actions/workflows/ghcr_deploy.yml/dispatches" \
              -d "{\"ref\":\"main\", \"inputs\":{\"tag\":\"v${VERSION}\"}}"
    """
    new_version_name = f"v{version}-stable"
    response = requests.post(
        "https://api.github.com/repos/BerriAI/litellm/actions/workflows/ghcr_deploy.yml/dispatches",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        },
        json={"ref": "main", "inputs": 
              {
                "tag": new_version_name,
                "commit_hash": commit_hash
            }
        },
    )
    print("response: ", response)
    print("response.text: ", response.text)
    print("response.status_code: ", response.status_code)


# new_stable_release("1.34.22.dev15")


def get_release_commit_hash(version_number=None):
    github_token = os.getenv("GITHUB_TOKEN")
    print("getting release commit hash for ", version_number)
    version_number = str(version_number)
    if not version_number.startswith("v"):
        version_number = f"v{version_number}"
    g = Github(github_token)
    repo = g.get_repo(
        "BerriAI/litellm"
    )  # Replace with your repository's username and name

    print("getting release =", version_number, "from repo=", repo)

    release_info = repo.get_release(
        id=version_number
    )

    print(release_info)
    print(release_info.target_commitish)
    print("commit hash: ", release_info.target_commitish)
    return release_info.target_commitish



# get_release_commit_hash(
#     version_number="v1.34.28"
# )
