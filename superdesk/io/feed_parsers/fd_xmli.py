import datetime
import logging

from flask import current_app as app
from superdesk.errors import ParserError
from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers import XMLFeedParser
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.metadata.utils import is_normal_package
from superdesk.utc import utc
from lxml import etree

logger = logging.getLogger(__name__)

class XMLIFeedParser(XMLFeedParser):
    """
    Feed parser for the Escenix XMLI
    """
    NAME = 'xmli'

    label = 'Escenix XMLI Parser'

    def can_parse(self, xml):
        return xml.tag == 'NewsML'

    def parse(self, xml, provider=None):
        items = {}
        try:
            self.parse_news_identifier(items, xml)
            self.parse_newslines(items, xml)
            self.parse_news_management(items, xml)
            self.parse_metadata(items, xml)
            items['body_html'] = etree.tostring(
                xml.find('NewsItem/NewsComponent/ContentItem/DataContent/nitf/body/body.content'),
                encoding='unicode').replace('<body.content>', '').replace('</body.content>', '')

            return items
        except Exception as ex:
            raise ParserError.newsmlTwoParserError(ex, provider)
           

    def parse_news_identifier(self, items, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/Identification/NewsIdentifier'))
        items['guid'] = parsed_el['PublicIdentifier']
        items['version'] = parsed_el['RevisionId']
        items['ingest_provider_sequence'] = parsed_el['ProviderId']
        items['data'] = parsed_el['DateId']

    def parse_news_management(self, items, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/NewsManagement'))
        if parsed_el.get('NewsItemType') != None:
            items['newsitemtype'] = parsed_el['NewsItemType']['FormalName']
        if parsed_el.get('ThisRevisionCreated') != None:
            items['versioncreated'] = self.datetime(parsed_el['ThisRevisionCreated'])
        if parsed_el.get('FirstCreated') != None:
            items['firstcreated'] = self.datetime(parsed_el['FirstCreated'])
        if parsed_el.get('Status') != None:
            items['pubstatus'] = (parsed_el['Status']['FormalName']).lower()

    def parse_newslines(self, items, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/NewsComponent/NewsLines'))   
        items['headline'] = parsed_el.get('HeadLine', '')
        items['slugline'] = parsed_el.get('SlugLine', '')
        items['byline'] = parsed_el.get('ByLine', '')
        items['copyrightline'] = parsed_el.get('CopyrightLine', '')
    
    def parse_metadata(self, items, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/NewsComponent/Metadata'))
        items['metadatatype'] = parsed_el['MetadataType']['FormalName']
        propertites = tree.findall('NewsItem/NewsComponent/Metadata/Property')
        for i in propertites:
            if i.get('FormalName', '') == 'DateLine':
                self.set_dateline(items, text=i.get('Value', ''))
            elif i.get('FormalName', '') != '':
                items[(i.get('FormalName')).lower()] = i.get('Value', '')

    def parse_elements(self, tree):
        items = {}
        for item in tree:
            if item.text is None:
                # read the attribute for the items
                if item.tag != 'HeadLine':
                    items[item.tag] = item.attrib
            else:
                # read the value for the items
                items[item.tag] = item.text
        return items

    def datetime(self, string):
        try:
            return datetime.datetime.strptime(string, '%Y%m%dT%H%M%S+0100')
        except ValueError:
            return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.0').replace(tzinfo=utc)

register_feed_parser(XMLIFeedParser.NAME, XMLIFeedParser())