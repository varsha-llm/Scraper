import scrapy
import json


class WhoPdfSpider(scrapy.Spider):
    name = "who_pdf"

    
    def start_requests(self):
     
        base_url_front= "https://iris.who.int/server/api/discover/search/objects?sort=dc.date.issued,DESC&page="
        base_url_back="&size=10&f.has_content_in_original_bundle=true,equals&embed=thumbnail&embed=item%2Fthumbnail"
        
        # Loop from page 0 to 2634
        for page in range(2635): 
            yield scrapy.Request(url=f"{base_url_front}{page}{base_url_back}", callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        
        # 1. Loop through documents on the current page
        objects = data.get('_embedded', {}).get('searchResult', {}).get('_embedded', {}).get('objects', [])
        for obj in objects:
            item_uuid = obj.get('_embedded', {}).get('indexableObject', {}).get('uuid')
            if item_uuid:
                bundle_url = f"https://iris.who.int/server/api/core/items/{item_uuid}/bundles"
                yield scrapy.Request(bundle_url, callback=self.parse_bundles)

    
    def parse_bundles(self, response):
        data = json.loads(response.text)
        bundles = data.get('_embedded', {}).get('bundles', [])
        
        for bundle in bundles:
          # Bitstream are always in the 'ORIGINAL' bundle
             if bundle.get('name') == 'ORIGINAL':
                 bitstream_link=bundle['_links']['bitstreams']['href']
                 
                 yield scrapy.Request(url=bitstream_link, callback=self.parse_bitstream_content)

    def parse_bitstream_content(self, response):
       
           content_json = json.loads(response.text)
        
           document=content_json['_embedded']['bitstreams'][0]['_links']['content']['href']

           yield {
           'file_urls': [document], 
           'original_name': content_json['_embedded']['bitstreams'][0]['id'] 
    }
   

       