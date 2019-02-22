# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from werkzeug.datastructures import ImmutableMultiDict
from superdesk.tests import TestCase
from superdesk import get_resource_service
from eve.utils import ParsedRequest


class ConceptItemsServiceTestCase(TestCase):
    concept_items = [
        {
            "name": "Hobbit",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "tolkien"],
            "language": "en",
            "definition": "The Hobbit is a children's fantasy novel by English author J. R. R. Tolkien."
        },
        {
            "name": "Lord of the rings",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "tolkien"],
            "language": "en",
            "definition": "The Lord of the rings is a children's fantasy novel by English author J. R. R. Tolkien."
        },
        {
            "name": "Bootstrap: Responsive Web Development",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "Jake Spurlock", "Development"],
            "language": "en",
            "definition": "Discover how easy it is to design killer interfaces and "
                          "responsive websites with the Bootstrap framework. "
        },
        {
            "name": "The Little Prince",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "Antoine de Saint-Exupéry"],
            "language": "en",
            "definition": "is a novella, the most famous work of French aristocrat, writer, poet, and pioneering "
                          "aviator Antoine de Saint-Exupéry."
        },
        {
            "name": "the Elegance of the Hedgehog",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "Muriel Barbery"],
            "language": "en",
            "definition": "A novel about parallels and the concealment of one’s true passions in life."
        },
        {
            "name": "and then there were none",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "Agatha Christie"],
            "language": "en",
            "definition": "Dame Agatha Mary Clarissa Christie, Lady Mallowan, DBE "
                          "(née Miller; 15 September 1890 – 12 January 1976) was an English writer."
        },
        {
            "name": "A Message to Garcia",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "Elbert Hubbard"],
            "language": "en",
            "definition": "A Message to Garcia is a widely distributed essay written by Elbert Hubbard in 1899, "
                          "expressing the value of individual initiative and conscientiousness in work."
        },
        {
            "name": "Гайдамаки",
            "cpnat_type": "cpnat:abstract",
            "labels": ["book", "Шевченко Тарас Григорович"],
            "language": "en",
            "definition": "Гайдамаки — історико-героїчна поема Шевченка, перший український історичний роман у віршах."
        }
    ]

    def setUp(self):
        with self.app.app_context():
            self.app.data.insert('concept_items', self.concept_items)

    def test_query_all_items(self):
        service = get_resource_service('concept_items')

        self.assertTrue(
            len(list(service.get_from_mongo(req=None, lookup={}))),
            len(self.concept_items)
        )

    def test_query_sort_by_name_case_sensetive(self):
        service = get_resource_service('concept_items')
        names = ['A Message to Garcia', 'Bootstrap: Responsive Web Development', 'Hobbit', 'Lord of the rings',
                 'The Little Prince', 'and then there were none', 'the Elegance of the Hedgehog', 'Гайдамаки']

        req = ParsedRequest()
        req.sort = 'name'
        cursor = service.get_from_mongo(req=req, lookup={})
        self.assertEqual(
            [i['name'] for i in cursor],
            names
        )

        req = ParsedRequest()
        req.sort = '-name'
        names.reverse()
        cursor = service.get_from_mongo(req=req, lookup={})
        self.assertEqual(
            [i['name'] for i in cursor],
            names
        )

    def test_query_sort_by_name_case_insensetive(self):
        service = get_resource_service('concept_items')
        names = ['A Message to Garcia', 'and then there were none', 'Bootstrap: Responsive Web Development', 'Hobbit',
                 'Lord of the rings', 'the Elegance of the Hedgehog', 'The Little Prince', 'Гайдамаки']

        req = ParsedRequest()
        req.sort = 'name'
        req.args = ImmutableMultiDict([('collation', '{"locale": "en", "strength":"1"}')])
        cursor = service.get_from_mongo(req=req, lookup={})
        self.assertEqual(
            [i['name'] for i in cursor],
            names
        )

        req = ParsedRequest()
        req.sort = '-name'
        req.args = ImmutableMultiDict([('collation', '{"locale": "en", "strength":"1"}')])
        names.reverse()
        cursor = service.get_from_mongo(req=req, lookup={})
        self.assertEqual(
            [i['name'] for i in cursor],
            names
        )

