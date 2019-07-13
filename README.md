Barebones working Python UDP server for games. 
Features two threads, one for input and one for output. Scales much better with clients than one thread per.
Client in Godot.

Ripped from another project so probably not exactly in a working state right now. Two big notes is that there's no reliability for packet loss yet, it's not very optimzed, and the server doesn't manage its own send rate.
