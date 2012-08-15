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
print '<thead><td>Partner Name</td><td>Portfolio Yield</td><td>Risk Rating</td></thead>'
print '<tbody>'
for p in sorted_partners:
    print '  <td>'
    print '    <tr><a href="%s">%s</a></tr>' % (p['url'], p['name'])
    if 'N/A' == p['yield']:
        print '    <tr>%s</tr>' % (p['yield'])
    else:
        print '    <tr>%s%%</tr>' % (p['yield'])
    if 'Non-Rated' == p['risk']:
        print '    <tr>%s</tr>' % (p['risk'])
    else:
        print '    <tr>%s stars</tr>' % (p['risk'])
    print '  </td>'
print '</tbody>'
print '</table>'
