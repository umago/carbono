carbono
=======

carbono is a small disk cloning tool which allows you to create
and restore images of your complete hard disk or partition.
Its also optimize the resulting image using tools to manipulate the 
filesystem and compacting the data blocks.

Requirements
------------

    * python
    * python-parted
    * ntfsprogs
    * dump
    * restore

Download and running
--------------------

1 - First you have to download the carbono livecd [here][2].

2 - Burn the .iso file to a CD/DVD or Convert to pendrive using [unetbootin][5] or a similar tool.

3 - Boot it.

Testing
-------

    WARNING: 
    DO NOT TEST CARBONO IN YOUR MAIN SYSTEM UNLESS YOU KNOW WHAT YOU ARE DOING.
    ITS HIGHLY RECOMMENDED USING VIRTUAL MACHINES WHEN TESTING CARBONO! NEVER FORGET IT!

blah blah blah

License
-------

carbono is distributed under the terms of the GNU General Public License, version 2.
See the [COPYING][4] file for more information.

Contributor list
----------------

Lucas Alvares Gomes (aka umago) <lucasagomes@gmail.com>

Contributing
------------

1. Fork it
2. Create a branch (`git checkout -b <branch name>`)
3. Commit your changes (`git commit -am "Added ..."`)
4. Push to the branch (`git push origin <branch name>`)
5. Create an [Issue][1] with a link to your branch

Please take a look at [TODO][3] file to see bugs and not-implemented-yet 
features.

[1]: http://github.com/umago/carbono/issues
[2]: http://umago.info/carbono
[3]: https://github.com/umago/carbono/blob/master/TODO
[4]: https://github.com/umago/carbono/blob/master/COPYING
[5]: http://unetbootin.sourceforge.net/
