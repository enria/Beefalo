import webbrowser
import requests
import re
import json
from datetime import datetime

from PyQt5.QtGui import QIcon, QPixmap
from bs4 import BeautifulSoup
from functools import lru_cache

from plugin_api import PluginInfo, ContextApi, SettingInterface, AbstractPlugin, get_logger
from result_model import ResultItem, ResultAction, MenuItem

log = get_logger("GitHub")

global proxy


@lru_cache(maxsize=256)
def get_icon(url):
    resp = requests.get(url, proxies=proxy)
    img = QPixmap()
    img.loadFromData(resp.content)
    return QIcon(img)


def pretty_date(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.utcnow()
    diff = now - time
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "  " + "just now"
        if second_diff < 60:
            return "  " + str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "  " + "a minute ago"
        if second_diff < 3600:
            return "  " + str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "  " + "an hour ago"
        if second_diff < 86400:
            return "  " + str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "  " + "Yesterday"
    if day_diff < 7:
        return "  " + str(day_diff) + " days ago"
    if day_diff < 31:
        return "  " + str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return "  " + str(day_diff // 30) + " months ago"
    return "  " + str(day_diff // 365) + " years ago"


class RepositoryItem(ResultItem):
    def __init__(self, plugin_info, repo: dict):
        star = ""
        if "stargazers_count" in repo:
            star = " %s   " % repo["stargazers_count"]
        language = ""
        if repo.get("language"):
            language = " %s   " % repo["language"]
        desc = ""
        if repo.get("description"):
            desc = " %s" % repo["description"]
        action = ResultAction(webbrowser.open, True, "https://github.com/" + repo["full_name"])
        super().__init__(plugin_info, repo["full_name"], "{}{}{}".format(star, language, desc),
                         "images/github_repository.png", action)
        if repo["private"]:
            self.icon = "images/github_repository_private.png"
        issue_action = ResultAction(webbrowser.open, True, "https://github.com/{}/issues".format(repo["full_name"]))
        self.menus = [MenuItem(" Issues", issue_action)]


class EventItem(ResultItem):
    def __init__(self, plugin_info, event: dict):
        desc = ""
        if event["type"] in ["CreateEvent", "WatchEvent"]:
            desc = "{} {} {}".format(event["actor"]["display_login"],
                                     event["payload"].get("action"),
                                     event["repo"]["name"])
        if event["type"] == "IssuesEvent":
            desc = "{} {} {}".format(event["actor"]["display_login"],
                                     event["payload"].get("action"),
                                     event["payload"]["issue"]["title"])
        if event["type"] == "IssueCommentEvent":
            desc = "{} comment \"{}\"".format(event["actor"]["display_login"],
                                              event["payload"]["issue"]["body"])
        if event["type"].startswith("Issue"):
            action = ResultAction(webbrowser.open, True, event["payload"]["issue"]["html_url"])
        else:
            action = ResultAction(webbrowser.open, True, "https://github.com/" + event["repo"]["name"])
        super().__init__(plugin_info, event["repo"]["name"], desc,
                         "images/github_icon.png", action)


class GitHubPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("GitHub", "GitHub tools", "images/github_icon.png", ["ghb"], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.user_name, self.user_token, self.proxy = "", "", {}
        self.load_setting()

    def query(self, keyword, text, token=None, parent=None):
        text = text.strip()
        if text:
            self.api.change_results([])
            if text.startswith("all:"):
                results = self.my_activity()
            elif text.startswith("note:"):
                results = self.recent_activity()
            elif text.startswith("repo:"):
                results = self.my_repositories()
            elif text.startswith("trend:"):
                results = self.github_trending()
            else:
                search_in_page = ResultItem(self.meta_info, "Search \"{}\" in GitHub website".format(text), text,
                                            "images/github_icon.png",
                                            ResultAction(webbrowser.open, True, "https://github.com/search?q=" + text))
                search_repository = ResultItem(self.meta_info, "Search Repository ",
                                               text,
                                               "images/github_icon.png",
                                               ResultAction(self.search_repository, False, text))
                results = [search_repository, search_in_page]
            return results
        else:
            home = ResultItem(self.meta_info, "Home",
                              "My (%s) GitHub home page" % self.user_name,
                              "images/github_icon.png",
                              ResultAction(webbrowser.open, True, "https://github.com/"))
            feeds = ResultItem(self.meta_info, "Notifications",
                               "My (%s) all notifications" % self.user_name,
                               "images/github_notifations.png",
                               ResultAction(self.api.change_query, False, "{} note:".format(keyword)))
            events = ResultItem(self.meta_info, "All activity",
                                "My (%s) all activity" % self.user_name,
                                "images/github_friends.png",
                                ResultAction(self.api.change_query, False, "{} all:".format(keyword)))
            repositories = ResultItem(self.meta_info, "Repositories",
                                      "My (%s) repositories" % self.user_name,
                                      "images/github_repository.png",
                                      ResultAction(self.api.change_query, False, "{} repo:".format(keyword)))
            trending = ResultItem(self.meta_info, "Trending",
                                  "See what the GitHub community is most excited about today.",
                                  "images/github_trending.png",
                                  ResultAction(self.api.change_query, False, "{} trend:".format(keyword)))
            return [home, feeds, events, repositories, trending]

    def search_repository(self, name):
        url = "https://api.github.com/search/repositories"
        try:
            repos = []
            for p in range(1):
                resp = requests.get(url, {"q": name, "page": p + 1}, proxies=self.proxy)
                if resp.status_code == 200:
                    repos += json.loads(resp.text)["items"]
            results = []
            for repo in repos:
                results.append(RepositoryItem(self.meta_info, repo))
            results.append(ResultItem(self.meta_info, "Search \"{}\" in GitHub website".format(name), name,
                                      "images/github_icon.png",
                                      ResultAction(webbrowser.open, True, "https://github.com/search?q=" + name)))
            self.api.change_results(results)
        except BaseException as e:
            log.error(e)

    def recent_activity(self):
        icons = {"Issue": "images/github_comment.png",
                 "RepositoryVulnerabilityAlert": "images/github_alert.png",
                 "PullRequest": "images/github_pull.png"}
        url = "https://api.github.com/notifications?all=true"
        try:
            resp = requests.get(url, headers={"Authorization": "token " + self.user_token}, proxies=self.proxy)
            if resp.status_code == 200:
                results = []
                activities = json.loads(resp.text)
                for activity in activities:
                    item = ResultItem(self.meta_info, activity["subject"]["title"])
                    item.action = ResultAction(webbrowser.open, True,
                                               "https://github.com" + activity["subject"]["url"].replace(
                                                   "https://api.github.com/repos", ""))
                    item.icon = icons[activity["subject"]["type"]]
                    item.subTitle = "{}    {}".format(activity["repository"]["full_name"]
                                                      , pretty_date(datetime.strptime(activity["updated_at"],
                                                                                      "%Y-%m-%dT%H:%M:%SZ")))
                    results.append(item)
                return results
        except BaseException as e:
            log.error(e)
        return []

    def my_activity(self):
        url = "https://api.github.com/users/{}/received_events".format(self.user_name)
        try:
            events = []
            resp = requests.get(url, headers={"Authorization": "token " + self.user_token}, proxies=self.proxy)
            if resp.status_code == 200:
                events = json.loads(resp.text)
            results = []
            for event in events:
                results.append(EventItem(self.meta_info, event))
            return results
        except BaseException as e:
            log.error(e)
        return []

    def my_repositories(self):
        url = "https://api.github.com/user/repos"
        try:
            repos = []
            resp = requests.get(url, headers={"Authorization": "token " + self.user_token}, proxies=self.proxy)
            if resp.status_code == 200:
                repos = json.loads(resp.text)
            results = []
            for repo in repos:
                results.append(RepositoryItem(self.meta_info, repo))
            return results
        except BaseException as e:
            log.error(e)
        return []

    def github_trending(self):
        url = "https://github.com/trending"
        try:
            repos = []
            resp = requests.get(url, proxies=self.proxy)
            if resp.status_code == 200:
                dom = BeautifulSoup(resp.text, "html.parser")
                items = dom.select("article.Box-row")
                for ele in items:
                    repo = {"full_name": re.sub(r"\s?/\s?", "/", re.sub(r"\s{2,}", " ", ele.select(".lh-condensed")[
                        0].get_text().strip())),
                            "private": False}
                    if ele.select(".f6 span.d-inline-block"):
                        repo["stargazers_count"] = ele.select(".f6 a.d-inline-block")[0].get_text().strip()
                    if ele.select(".f6 span.d-inline-block"):
                        repo["language"] = ele.select(".f6 span.d-inline-block")[0].get_text().strip()
                    if ele.select("p.text-gray"):
                        repo["description"] = ele.select("p.text-gray")[0].get_text().strip()
                    repos.append(repo)
            results = []
            for repo in repos:
                results.append(RepositoryItem(self.meta_info, repo))
            return results
        except BaseException as e:
            log.error(e)
        return []

    def load_setting(self):
        self.user_name = self.get_setting("user")["name"]
        self.user_token = "".join(self.get_setting("user")["token"])
        self.proxy = self.get_setting("proxy")
        global proxy
        proxy = self.proxy

    def reload(self):
        SettingInterface.reload(self)
        self.load_setting()
