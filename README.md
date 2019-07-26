Barebones working Python UDP server and client for games. It's starting to look okay.

Server features two threads, one for input and one for output. Scales much better with clients than one thread per. Client is a single thread, using select to manage i/o from the server. They both use the same Connection as datacontainers that they act as managers on.

Ripped from another project so probably not exactly in a working state right now. Biggest notes is that only the basics of reliability for packet loss have been implemented.
