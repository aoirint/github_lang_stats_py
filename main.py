import os
import json
import requests
from dataclasses import dataclass
from typing import Dict, List, Any

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ.get('TOKEN')
assert TOKEN


@dataclass
class Lang:
    name: str
    color: str
    size: int


@dataclass
class LangRepo:
    name: str
    size: int


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('login', type=str)
    args = parser.parse_args()

    login = args.login

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
                orderBy: {
                    field: PUSHED_AT
                    direction: DESC
                }
            ) {
                nodes {
                    name
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
            'login': login,
        },
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }

    res = requests.post(api_url, headers=headers, data=json.dumps(payload))

    print(res.status_code)
    if res.status_code != 200:
        raise Exception(res.text)

    responseData = res.json()
    data = responseData['data']

    repos = data['user']['repositories']['nodes']
    langDict: Dict[str, Lang] = {}
    lang2Repos: Dict[str, List[LangRepo]] = {}
    for repo in repos:
        repoName = repo['name']
        repoLangs = repo['languages']['edges']
        for repoLang in repoLangs:
            repoLangSize = repoLang['size']
            repoLangNode = repoLang['node']
            repoLangName = repoLangNode['name']
            repoLangColor = repoLangNode['color']

            if repoLangName not in langDict:
                langDict[repoLangName] = Lang(repoLangName, repoLangColor, 0)

            langDict[repoLangName].size += repoLangSize

            if repoLangName not in lang2Repos:
                lang2Repos[repoLangName] = []
            lang2Repos[repoLangName].append(LangRepo(repoName, repoLangSize))

    lang2Repos = {key: sorted(langRepos, key=lambda langRepo: langRepo.size, reverse=True) for key, langRepos in lang2Repos.items()}

    langs = list(sorted(langDict.values(), key=lambda lang: lang.size, reverse=True))
    for lang in langs:
        print(f'{lang.name}: {lang.size}')
        for langRepo in lang2Repos[lang.name]:
            print(f'    {langRepo.name}: {langRepo.size}')
