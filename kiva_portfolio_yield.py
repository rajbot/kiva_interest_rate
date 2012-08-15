#!/usr/bin/env python

"""
A quick and dirty script to find Kiva Field Partners who charge a low interest rate.
"""

import lxml.etree
import re
import time

partners_url = 'http://www.kiva.org/partners'
utf8_html_parser = lxml.etree.HTMLParser(encoding='utf-8')


def find_percent_yield(url):
    print 'parsing', url,
    page = lxml.etree.parse(url, parser=utf8_html_parser)

    infos = page.findall("//div[@class='info']")
    assert 1 == len(infos)
    info = infos[0]

    dl = info.find('dl')
    dts = dl.findall('dt')
    dds = dl.findall('dd')
    assert 14 == len(dts)
    assert 14 == len(dds)

    assert 'Interest & Fees are Charged' == dts[6].find('a').text

    interest_charged = dds[6].text
    assert ('Yes' == interest_charged) or ('No' == interest_charged)

    if 'No' == interest_charged:
        portfolio_yield = 0.0
    else:
        interest_table = page.find("//table[@id='stats-table-interest']")
        trs = interest_table.findall('tr')
        yield_tr = trs[1]
        portfolio_yield = yield_tr.find('td').text.strip().rstrip('%')

    print portfolio_yield

    time.sleep(2)
    return portfolio_yield


partner_array = []
partners = lxml.etree.parse(partners_url, parser=utf8_html_parser)
tbody = partners.find('//table/tbody')

for tr in tbody:
    tds = tr.findall('td')
    assert 5 == len(tds)

    info_td   = tds[0]
    risk_td   = tds[2]

    partner_a    = info_td.find('article/div/h1/a')
    partner_url  = partner_a.get('href')
    partner_name = partner_a.text

    partner_risk = risk_td.find('div').get('title')
    partner_risk = re.sub('^Partner Risk Rating:\s+', '', partner_risk)

    if 'Closed' == partner_risk:
        continue

    percent_yield = find_percent_yield(partner_url)

    partner_array.append({'url':  partner_url,
                          'name': partner_name,
                          'risk': partner_risk,
                          'yield': percent_yield,
                        })


sorted_partners = sorted(partner_array, key=lambda k: k['yield'])

#print sorted_partners

print '<table>'
print '<thead><tr><th>Partner Name</th><th>Portfolio Yield</th><th>Risk Rating</th></tr></thead>'
print '<tbody>'
for p in sorted_partners:
    print '  <tr>'
    print '    <td><a href="%s">%s</a></td>' % (p['url'], p['name'])
    if 'N/A' == p['yield']:
        print '    <td>%s</td>' % (p['yield'])
    else:
        print '    <td>%s%%</td>' % (p['yield'])
    if 'Non-Rated' == p['risk']:
        print '    <td>%s</td>' % (p['risk'])
    else:
        print '    <td>%s stars</td>' % (p['risk'])
    print '  </tr>'
print '</tbody>'
print '</table>'
