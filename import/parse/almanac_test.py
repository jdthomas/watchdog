#!/usr/bin/env python
# -*- coding: utf-8 -*-
import almanac, re, cgitb
cgitb.enable(format='text')

def ok(a, b): assert a == b, (a, b)
def ok_re(a, b): assert re.search(b, a), (a, b)

root = '../../data/crawl/almanac/nationaljournal.com/pubs/almanac/'

def test_scrape_person(scrape):
    trent_franks = scrape(root + '2004/people/az/rep_az02.htm')
    ok(trent_franks['name'], 'Trent Franks')
    ok(trent_franks['title'], 'Rep.')
    jim_bunning = scrape(root + '2008/people/ky/kys2.htm')
    ok(jim_bunning['name'], 'Jim Bunning')

    # A governor:
    janet_napolitano = scrape(root + '2004/people/az/azgv.htm')
    ok(janet_napolitano['name'], 'Janet Napolitano')
    ok(janet_napolitano['title'], 'Gov.')

    # "Representative at large", "R-At Large"
    don_young = scrape(root + '2004/people/ak/rep_ak01.htm')
    ok(don_young['name'], 'Don Young')
    ok(don_young['party'], 'R')

    # I have no idea what "DFL" means, and I'm not sure whether it's
    # an abbreviation for a political party or not.  I've also seen
    # "CFL" in Lieberman's page.
    mark_dayton = scrape(root + '2004/people/mn/mns1.htm')
    ok(mark_dayton['name'], 'Mark Dayton')
    ok(mark_dayton['party'], 'DFL')

    # This one is actually wrong; the guy's name is
    # Rubén Hinojosa, not
    # Ruben Hinojosa.  But the accent is missing in the file.
    hinojosa = scrape(root + '2004/people/tx/rep_tx15.htm')
    ok(hinojosa['name'], 'Ruben Hinojosa')

    # The junior Senator from Connecticut thinks he's an "Independent
    # Democrat".
    lieberman = scrape(root + '2008/people/ct/cts2.htm')
    ok(lieberman['name'], 'Joe Lieberman')
    ok(lieberman['party'], 'ID')

    #@@ currently can't find photo in
    # 2004/people/wi/rep_wi09.htm

    # Unusual title: "Del.", for "delegate" (from Guam)
    madeleine_bordallo = scrape(root + '2006/people/gu/rep_gu01.htm')
    ok(madeleine_bordallo['name'], 'Madeleine Bordallo')

    # Office locations.
    ok_re(trent_franks['dcoffice'], '202-225-4576')
    ok_re(jim_bunning['dcoffice'], '202-224-4343')

    # Religion
    ok(trent_franks['religion'], 'Baptist')

    # Older files.
    robert_byrd = scrape(root + '2000/people/wv/wvs1.htm')
    ok(robert_byrd['name'], 'Robert C. Byrd')

    # President
    pres = scrape(root + '2000/people/president.htm')
    # ...but there's no code to get anything useful out of that yet.

    # Jesse Ventura: Independent Party
    wrestler = scrape(root + '2002/people/mn/mngv.htm')
    ok(wrestler['name'], 'Jesse Ventura')

    # Proper handling of <br> tags.
    steve_pearce = scrape(root + '2008/people/nm/rep_nm02.htm')
    ok(steve_pearce['name'], 'Steve Pearce')
    ok_re(steve_pearce['stateoffice'], r'505-392-8325;\s+Las Cruces')

    # Quotes around magical image height of 117
    gordon_smith = scrape(root + '2000/people/or/ors2.htm')
    ok(gordon_smith['name'], 'Gordon H. Smith')
    ok_re(gordon_smith['dcoffice'], r'202-224-3753')

    # Some inconsistency.  This is the same guy in the same district.
    # "The 5th Congressional District of Wisconsin, numbered the 9th
    # before 2002 redistricting..."
    sensenbrenner_1 = scrape(root + '2006/people/wi/rep_wi05.htm')
    ok(sensenbrenner_1['name'], 'Jim Sensenbrenner')
    sensenbrenner_2 = scrape(root + '2002/people/wi/rep_wi09.htm')
    ok(sensenbrenner_2['name'], 'F. James Sensenbrenner Jr.')

    # Aaron says:
    # The data I was really hoping to get, though, were the numbers at
    # the bottom, especially the previous years' election results, and
    # district size, density, and income numbers.

    ## Election results:
    # plain HTML version
    #jim_bunning_elections = jim_bunning['electionresults_html']
    #ok_re(jim_bunning_elections, r'873,507')

    jbe2 = jim_bunning['electionresults']
    ok(jbe2[0], { 'election': '2004 general',
                  'candidate': 'Jim Bunning (R)',
                  'totalvotes': '873,507',
                  'percent': '51%',
                  'expenditures': '$6,075,399' })
    ok(jbe2[1], { 'election': '2004 general',
                  'candidate': 'Daniel Mongiardo (D)', 
                  'totalvotes': '850,855',
                  'percent': '49%',
                  'expenditures': '$3,104,981' })
    ok(jbe2[2]['election'], '2004 primary')
    ok(jbe2[2].get('expenditures'), None) # not known
    ok(jbe2[6]['candidate'], 'Other')

    ok(trent_franks['electionresults'][2], 
       {'election': '2002 general', 
        'candidate': 'Edward Carlson (Lib)',
        'totalvotes': '5,919',
        'percent': '4%' })

    ok(janet_napolitano['electionresults'][9],
       {'election': '1998 general',
        'candidate': 'Paul Johnson (D)',
        'totalvotes': '361,552',
        'percent': '36%'})

    # At present the code doesn't deal with the headerless tables from
    # the 2000 'wrestler' and 'robert_byrd' pages.  Dealing with those
    # will presumably require guessing column meanings from their
    # contents.

    sper = steve_pearce['electionresults']
    ok(sper[0], {'election': '2006 general', 
                 'candidate': 'Steve Pearce (R)', 
                 'totalvotes': '92,620',
                 'percent': '59%', 
                 'expenditures': '$1,349,394'})
    #@@ here's what it says in the table, but this is an ontological error:
    ok(sper[2]['totalvotes'], 'Unopposed')

    ## District demographics
    demog = steve_pearce['demographics']
    ok(demog['Area size'], '69,598 sq. mi.')
    ok(demog['Ancestry'], 'German: 7.4%; English: 5.9%; Irish: 5.7%;')
    ok(demog['Poverty status'], '22.4%')
    ok(demog['Median income'], '$29,269')

    ## interest group ratings
    ratings = steve_pearce['interest_group_rating']
    ok(ratings['2006']['ADA'], 5)
    ok(ratings['2005']['ADA'], 0)
    ok(ratings['2006']['ACLU'], 18)
    ok('ACLU' in ratings['2005'], False)  # value in HTML is '-'

    ok(sensenbrenner_1['interest_group_rating']['2004']['NTU'], 83)
    ok(jim_bunning['interest_group_rating']['2006']['FRC'], 87)

def test_scrape_state(scrape):
    ## State demographics
    north_dakota = scrape(root + '2008/states/nd/index.html')
    ok(north_dakota['state']['Pop. 2006 (est)'], '635,867')
    ok(north_dakota['state']['Poverty status'], '11.9%')
    ok(north_dakota['state']['Median income'], '$34,604')

if __name__ == '__main__':
    test_scrape_person(almanac.scrape_person)
    test_scrape_state(almanac.scrape_state)
