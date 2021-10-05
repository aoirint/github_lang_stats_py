import os
import json
import requests

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ.get('TOKEN')
assert TOKEN

if __name__ == '__main__':
    api_url = 'https://api.github.com/graphql'

    query = """
    query GetLangStats(
        $login: String!
    ) {
        user(login: $login) {
            repositories(
                ownerAffiliations: OWNER
                isFork: false
                first: 100
            ) {
                nodes {
                    languages(
                        first: 10
                        orderBy: {
                            field: SIZE
                            direction: DESC
                        }
                    ) {
                        edges {
                            size
                            node {
                                color
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """

    payload = {
        'query': query,
        'variables': {
            'login': 'aoirint',
        },
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }

    res = requests.post(api_url, headers=headers, data=json.dumps(payload))

    print(res.status_code)
    print(res.json())
