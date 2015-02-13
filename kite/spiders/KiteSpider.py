import re
from scrapy import FormRequest, Selector, Request
from scrapy.spider import BaseSpider
from kite.items import KiteItem
from kite.utils.regex import Regex
from scrapy import log

__author__ = 'tuly'


class KiteSpider(BaseSpider):
    name = 'kite'
    allowed_domains = ['kitefinder.com']
    regex = Regex()
    # start_urls = ['http://www.kitefinder.com/en/kites/search']

    def start_requests(self):
        log.start(logfile='kite.log')
        return [self.request_pagination()]

    def request_pagination(self, page=1):
        post_data = {'beginner-search': 'false',
                     'offset': str(page),
                     'order': 'desc',
                     'sortby': 'date',
                     'values[213][max]': '100',
                     'values[213][min]': '0',
                     'values[306][max]': '100',
                     'values[306][min]': '0',
                     'values[31][max]': '100',
                     'values[31][min]': '0',
                     'values[33][max]': '100',
                     'values[33][min]': '0',
                     'values[34][max]': '100',
                     'values[34][min]': '0',
                     'values[35][max]': '100',
                     'values[35][min]': '0',
                     'values[36][max]': '100',
                     'values[36][min]': '0',
                     'values[37][max]': '100',
                     'values[37][min]': '0',
                     'values[38][max]': '100',
                     'values[38][min]': '0',
                     'values[41][max]': '100',
                     'values[41][min]': '0',
                     'values[42][max]': '100',
                     'values[42][min]': '0',
                     'values[43][max]': '100',
                     'values[43][min]': '0',
                     'values[44][max]': '100',
                     'values[44][min]': '0',
                     'values[45][max]': '100',
                     'values[45][min]': '0',
                     'values[47][max]': '100',
                     'values[47][min]': '0',
                     'values[48][max]': '100',
                     'values[48][min]': '0',
                     'values[49][max]': '100',
                     'values[49][min]': '0',
                     'values[50][max]': '100',
                     'values[50][min]': '0',
                     'values[59][max]': '100',
                     'values[59][min]': '0',
                     'values[5][max]': '100',
                     'values[5][min]': '0',
                     'values[60][max]': '100',
                     'values[60][min]': '0',
                     'values[61][max]': '100',
                     'values[61][min]': '0',
                     'values[62][max]': '100',
                     'values[62][min]': '0',
                     'values[budget][currency]': 'EUR',
                     'values[budget][max]': '3000',
                     'values[budget][min]': '0'}
        header = {'Accept': 'text/html, */*',
                  'Connection': 'keep-alive',
                  'Host': 'www.kitefinder.com',
                  'Referer': 'http://www.kitefinder.com/en/kites',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0',
                  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  'X-Requested-With': 'XMLHttpRequest'}
        return FormRequest('http://www.kitefinder.com/en/kites/search',
                           meta={'page': page}, method='POST',
                           formdata=post_data, headers=header,
                           callback=self.parse)

    def parse(self, response):
        selector = Selector(response)
        product_urls = selector.xpath('//div[@class="kite-caption"]/h2/a/@href').extract()
        for url in product_urls:
            yield Request(url, meta={'url': url}, callback=self.parseDetails)

        #check next page
        print 'Checking if it has next page.'
        next_page = selector.xpath('//a[@class="next"]/@href').extract()
        if next_page and next_page != '':
            current_page = response.meta['page']
            self.log('Requesting for next page: [%d]' % (int(current_page) + 1), log.DEBUG)
            yield self.request_pagination(int(current_page) + 1)
        else:
            print 'There is no more next pages.'

    def parseDetails(self, response):
        try:
            url = response.meta['url']
            print 'URL: %s' % url
            kite = KiteItem()
            selector = Selector(response)
            details = selector.xpath(
                '//div[@id="tabs"]//div[@id="specifications"]//table[@cellspacing="1"]/tr').extract()
            brand = ''
            for tr in details:
                tr = re.sub(r'\n+', ' ', tr)
                tr = re.sub(r'\s+', ' ', tr)
                # <tr> <th>Riding type:</th> <td> Freeride/Allround </td> </tr>
                if self.regex.isFoundPattern(r'(?i)<tr>\s*<th>Riding type:</th>\s*<td>([^<]*)</td>', tr):
                    kite['riding_type'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Riding type:\s*</th>\s*<td>([^<]*)</td>', tr).strip()
                # <tr> <th>Year:</th> <td itemprop="identifier"> 2015 </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>Year:</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['year'] = self.regex.getSearchedData(r'(?i)<tr>\s*<th>Year:</th>\s*<td[^>]*>([^<]*)</td>',
                                                              tr).strip()
                # <tr> <th>Brand:</th> <td itemprop="brand"> Naish kiteboarding </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Brand:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    brand = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Brand:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                    kite['brand'] = brand
                # <tr> <th>Size:</th> <td> 07m, 09m, 10.5m, 12m, 14m, 17m </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Size:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['size'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Size:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Type:</th> <td> SLE </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Type:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['type'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Type:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>One pump:</th> <td> Yes </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*One pump:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['one_pump'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*One pump:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Bridles:</th> <td> Yes </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Bridles:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['bridles'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Bridles:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Number of struts:</th> <td> 5 </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Number of struts:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                                               tr):
                    kite['num_of_struts'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Number of struts:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Colours:</th> <td> Various </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Colours:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['colors'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Colours:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Line length:</th> <td> 20m - 24m - 27m </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Line length:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['line_length'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Line length:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Bar length:</th> <td> 45cm-51cm </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Bar length:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['bar_length'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Bar length:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Bar:</th> <td> 4 lines </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Bar:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['bar'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Bar:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Depower:</th> <td> Clamcleat </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Depower:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['depower'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Depower:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Safety:</th> <td> Push </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Safety:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['safety'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Safety:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Swivel:</th> <td> Yes </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Swivel:\s*</th>\s*<td[^>]*>([^<]*)</td>', tr):
                    kite['swivel'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Swivel:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Variable bar length:</th> <td> Yes </td> </tr>
                elif self.regex.isFoundPattern(
                        r'(?i)<tr>\s*<th>\s*Variable bar length:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr):
                    kite['variable_bar_length'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Variable bar length:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
                # <tr> <th>Oh shit handles:</th> <td> No </td> </tr>
                elif self.regex.isFoundPattern(r'(?i)<tr>\s*<th>\s*Oh shit handles:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                                               tr):
                    kite['oh_shit_handles'] = self.regex.getSearchedData(
                        r'(?i)<tr>\s*<th>\s*Oh shit handles:\s*</th>\s*<td[^>]*>([^<]*)</td>',
                        tr).strip()
            model = url.split('/')[-1]
            model = re.sub(r'\d+', '', model)
            model = re.sub(r'-', ' ', model)
            brands = brand.split(' ')
            for b in brands:
                model = re.sub(r'(?i)%s' % b, '', model)
            kite['model'] = model.strip()
            kite['link'] = url
            return kite
        except Exception, x:
            print x
