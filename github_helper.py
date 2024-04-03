import requests 
import os
import dotenv
from dotenv import load_dotenv
load_dotenv()


def new_stable_release(version):
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
        json={"ref": "main", "inputs": {"tag": new_version_name}},
    )
    print("response: ", response)
    print("response.text: ", response.text)
    print("response.status_code: ", response.status_code)


# new_stable_release("1.34.22.dev15")
