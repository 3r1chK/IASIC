# IASIC

_**I**nstagram **A**utomatic **S**ampler And **I**mageNet **C**lassifier_ is a simple tool to automatically 
retrieve photo by the _Instagram API_, to elaborate them and to store the result in a persistent database.

---

## Installation

### Pre-Requisites
- _IASIC_ is wrote for _Python3_ and uses the following packages:
  - os
  - time
  - datetime
  - requests
  - urllib
  - json
  - PIL
  - hashlib
  - tensorflow
  - numpy
  - mysql.connector
  - threading
 
### SQL Database
_IASIC_ also needs a _SQL-db_ to store predictions outputs. 
Install _mysql-server_ and then run `db/install.sql` on it.
You also have to put the server login data into `config/db.txt` as follows:
- **server address** in the first line;
- **login name** in the second line;
- **login password** in the third line;
- **server port** in the fourth line (by default it should be 3306);
- **database name** in the fifth line (if you didn't modified it you can leave this as it's). 


### Configuration and first Run
Now you've to choose _hashtags_ and/or _usernames_ to be used as search key and a relative period,
which will be the sampling period - expressed in minutes - on that search key.
Once choice, put each couple `search_key period` (_i.e. "search_key[SAPCE]period_") in a line of `config/config.txt` that will be something like this:
```
#naples 1
@zerounoquarantaquattro 20
#seaside 3
#shark 4
```
_(this would initializes 4 auto-samplers: one will sample every minute searching for "naples" _hashtag_, another will sample every 20 minutes searching for the user "zerounoquarantaquattro", and so on)_

The only thing left to do is to open your console and to run `auto-sampler.py` with the Python3 interpreter, so to make the sampling start.

---

### Author
- Erich Kohmann - [@gmail.com](mailto:erich.kohmann@gmail.com), [@github.com](https://github.com/3richK)

### Contributors
- _None_

### License
_IASIC_ is licensed under the _GNU General Public License v3.0_.
