We we able to find all of the flags using our single-threaded web crawler. There are two main
parts of the web crawler: login and searching for the flags.

The login part includes the initial GET and POST requests to ensure that the user can log into
Fakebook. The user first gets the Fakebook login page, then POSTs their information, and
finally GETs the response that say they are logged in. We struggled with getting the format of
the HTTPS requests at first. We also struggle with identifying the right headers to use in the
requests.

The second part includes our simple algorithm to find the flags on hidden in the webpage.
Our search is essentially a bread-first algorithm which gets all of the links found on a page
and adds it to a queue. After going through a page, the algorithm hops to the next item in
the queue. In this part we struggled with get the correct values for the links. This led us
to attempt to request from sites outside of the Fakebook domain.