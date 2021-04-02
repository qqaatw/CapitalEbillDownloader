import re

from bs4 import BeautifulSoup

class BillParser:
    def __init__(self, html):
        self.renew(html)

    def _parse_table(self, table_obj):
        data = []
        headers = None
        for idx, element in enumerate(table_obj.find_all("tr")):
            if idx == 0:
                section_name = element.text
                continue

            sub_data = [''] # For date indicator column
            for sub_element in element.find_all("td", recursive=False):
                if len(sub_element) > 1 and headers is None:
                    sub_data.extend([i.text.strip() for i in sub_element])
                else:
                    sub_data.append(sub_element.get_text().strip())

            if len(sub_data) > 2:
                if headers is None:
                    # Replace 商品明細 with 月份 中文代號 英文代號
                    try:
                        product_detail_idx = sub_data.index('商 品 明 細')
                        sub_data = sub_data[0:product_detail_idx] + \
                                   ['月份', 'N/A','中文代號', '英文代號'] + \
                                   sub_data[product_detail_idx+1:]
                    except:
                        pass

                    headers = sub_data 
                else:
                    data.append(sub_data)
        
        return section_name, headers, data

    def parse_available_dates(self):
        dates = []
        for date in self.soup.select('select[name="data_YM"] > option'):
            dates.append(date.attrs['value'])

        return dates

    def parse_bill_tables(self, date):
        table_dict = {}

        for product_tables in self.soup.find_all('table'):
            if 'width' in product_tables.attrs and 'align' in product_tables.attrs:
                
                # Product name Eg. 期貨交易明細
                if product_tables.attrs['width'] == '100%' and product_tables.attrs['align'] == 'center':
                    idx = 0
                    product_name = re.sub('\xa0| ', '', product_tables.text)
                    if product_name == '公告訊息與個人訊息提示': 
                        break
            
                # Product content
                if product_tables.attrs['width'] == '710' and product_tables.attrs['align'] == 'center':
                    if idx == 0:
                        idx += 1  # Pass 證券&期貨帳號
                        continue 
                    section_name, headers, data = self._parse_table(product_tables)
                    
                    # Pass as an error occurs.
                    if re.search('原始保證金', section_name): continue

                    # Insert a date indicator.
                    data.insert(0, [date] + ['' for i in range(len(headers)-1)])

                    for item in data:
                        assert len(headers) == len(item), \
                            f"{section_name}'s header length is not equal to data length."

                    table_dict[f'{product_name}-{section_name}'] = {'headers':headers, 'data':data}
                    idx += 1
        return table_dict
    
    def renew(self, html):
        html = re.sub('\u3000', '', html)
        self.soup = BeautifulSoup(html, 'html.parser')

if __name__ == "__main__":
    pass