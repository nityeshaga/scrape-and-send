# Scrape and Send

A highly modular tool for scraping websites and notifying via email 
upon desired updates.

---------------

### What is it

Originally, I built this as a simple, ugly script to help my dad get 
notified about new business tenders on some government website.

Since then, I have modularised its code so that it is extremely simple
to add more websites. To add a new website, one only needs to write the
scraper class for it using his/her favourite Python library (I have 
used `mechanicalsoup` and `selenium`) and add that module to the 
[`scraper/`](https://github.com/nityeshaga/scrape-and-send/tree/master/scraper) 
directory.

The rest of the code can take care of sending email-alerts when the
scraper catches new updates.

---------------

### Next goal: 100% test coverage

I realise the importance of adding tests to the code and coming this
far with this project has only made that belief stronger. My next goal
is to add unittests and doctests for the entire codebase and get a test
coverage of 100% before I move to add new features.
