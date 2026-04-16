from apiBugzilla import Bugzilla
from bugzilla_tracker import BugzillaTracker

print(Bugzilla('abc').Url_Bugzilla)
print(Bugzilla('abc','https://vmbugzilla.altus.com.br').Url_Bugzilla)
print(Bugzilla('abc','https://vmbugzilla.altus.com.br/demandas').Url_Bugzilla)
print('imports OK')
